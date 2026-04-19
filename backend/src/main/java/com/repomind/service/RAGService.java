package com.repomind.service;

import com.repomind.config.OllamaConfig;
import com.repomind.dto.ChatResponse;
import com.repomind.repository.CodeChunkRepo;
import com.repomind.repository.CodeFileRepo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.*;
import java.util.stream.Collectors;

/**
 * RAG (Retrieval-Augmented Generation) service.
 * Performs similarity search against pgvector embeddings,
 * builds a context-rich prompt, and calls Ollama for generation.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class RAGService {

    private final CodeChunkRepo codeChunkRepo;
    private final CodeFileRepo codeFileRepo;
    private final WebClient ollamaWebClient;
    private final OllamaConfig ollamaConfig;

    @Value("${rag.top-k:5}")
    private int topK;

    @Value("${rag.max-context-length:6000}")
    private int maxContextLength;

    /**
     * Process a user question using the RAG pipeline:
     * 1. Generate query embedding via Ollama
     * 2. Similarity search in pgvector
     * 3. Build prompt with retrieved context
     * 4. Generate answer via Ollama
     */
    public ChatResponse.ChatResponseBuilder processQuestion(UUID repoId, String question) {
        log.info("RAG processing: repoId={}, question={}", repoId, question);

        // Step 1: Generate embedding for the query
        List<Double> queryEmbedding = generateQueryEmbedding(question);

        // Step 2: Similarity search
        String embeddingStr = queryEmbedding.toString();
        List<Object[]> results = codeChunkRepo.findSimilarChunks(repoId, embeddingStr, topK);

        // Step 3: Build citations and context
        List<ChatResponse.Citation> citations = new ArrayList<>();
        StringBuilder contextBuilder = new StringBuilder();

        for (Object[] row : results) {
            String chunkId = row[0].toString();
            UUID fileId = UUID.fromString(row[1].toString());
            String chunkType = row[3] != null ? row[3].toString() : "BLOCK";
            String chunkName = row[4] != null ? row[4].toString() : "unknown";
            String content = row[5] != null ? row[5].toString() : "";
            Integer startLine = row[6] != null ? ((Number) row[6]).intValue() : 0;
            Integer endLine = row[7] != null ? ((Number) row[7]).intValue() : 0;
            double distance = row[10] != null ? ((Number) row[10]).doubleValue() : 1.0;
            double relevanceScore = Math.round((1.0 - distance) * 1000.0) / 1000.0;

            // Get file path from code_files table
            String filePath = codeFileRepo.findById(fileId)
                    .map(f -> f.getFilePath())
                    .orElse("unknown");

            // Build citation
            String snippet = content.length() > 200
                    ? content.substring(0, 200) + "..."
                    : content;

            citations.add(ChatResponse.Citation.builder()
                    .chunkId(chunkId)
                    .filePath(filePath)
                    .chunkName(chunkName)
                    .chunkType(chunkType)
                    .startLine(startLine)
                    .endLine(endLine)
                    .relevanceScore(relevanceScore)
                    .snippet(snippet)
                    .build());

            // Add to context (with truncation)
            String contextEntry = String.format(
                "--- File: %s | %s: %s (lines %d-%d) ---\n%s\n\n",
                filePath, chunkType, chunkName, startLine, endLine, content
            );

            if (contextBuilder.length() + contextEntry.length() <= maxContextLength) {
                contextBuilder.append(contextEntry);
            }
        }

        // Step 4: Generate answer via Ollama
        String context = contextBuilder.toString();
        String answer = generateAnswer(question, context);

        return ChatResponse.builder()
                .answer(answer)
                .citations(citations);
    }

    /**
     * Generate an embedding vector for a search query using Ollama.
     */
    @SuppressWarnings("unchecked")
    private List<Double> generateQueryEmbedding(String text) {
        try {
            Map<String, Object> request = Map.of(
                "model", ollamaConfig.getEmbedModel(),
                "prompt", "Search query: " + text
            );

            Map<String, Object> response = ollamaWebClient.post()
                    .uri("/api/embeddings")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            if (response != null && response.containsKey("embedding")) {
                return (List<Double>) response.get("embedding");
            }

            log.warn("Empty embedding response from Ollama");
            return Collections.nCopies(ollamaConfig.getEmbeddingDim(), 0.0);

        } catch (Exception e) {
            log.error("Failed to generate query embedding: {}", e.getMessage());
            return Collections.nCopies(ollamaConfig.getEmbeddingDim(), 0.0);
        }
    }

    /**
     * Generate a grounded answer using Ollama chat with retrieved context.
     */
    @SuppressWarnings("unchecked")
    public String generateAnswer(String question, String context) {
        String systemPrompt = """
            You are RepoMind AI, an expert code analyst. You answer questions about a codebase
            using ONLY the provided code context. Follow these rules:

            1. Base your answer STRICTLY on the provided code snippets
            2. Reference specific file paths and function/class names
            3. If the context doesn't contain enough information, say so honestly
            4. Use code blocks when referencing specific code
            5. Be concise but thorough
            6. Mention file paths in your answer so the user can find the code
            """;

        String userPrompt = String.format("""
            ## Code Context
            %s

            ## Question
            %s

            Provide a detailed, grounded answer based on the code context above.
            """, context, question);

        try {
            Map<String, Object> request = Map.of(
                "model", ollamaConfig.getChatModel(),
                "messages", List.of(
                    Map.of("role", "system", "content", systemPrompt),
                    Map.of("role", "user", "content", userPrompt)
                ),
                "stream", false
            );

            Map<String, Object> response = ollamaWebClient.post()
                    .uri("/api/chat")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            if (response != null && response.containsKey("message")) {
                Map<String, Object> message = (Map<String, Object>) response.get("message");
                return message.getOrDefault("content", "I couldn't generate an answer.").toString();
            }

            return "I couldn't generate an answer. Please try again.";

        } catch (Exception e) {
            log.error("Failed to generate answer from Ollama: {}", e.getMessage());
            return "Error generating answer: " + e.getMessage();
        }
    }

    /**
     * Generate a specific insight about the repository (architecture, onboarding, flow).
     */
    public String generateInsight(UUID repoId, String insightType, String additionalContext) {
        // Retrieve diverse chunks for broader repository understanding
        List<Object[]> results = codeChunkRepo.getChunkTypeSummary(repoId);

        // Get representative chunks from each type
        String embeddingStr = Collections.nCopies(ollamaConfig.getEmbeddingDim(), 0.0).toString();
        List<Object[]> chunks = codeChunkRepo.findSimilarChunks(repoId, embeddingStr, 10);

        StringBuilder context = new StringBuilder();
        for (Object[] row : chunks) {
            String filePath = row[4] != null ? row[4].toString() : "";
            String content = row[5] != null ? row[5].toString() : "";
            String chunkType = row[3] != null ? row[3].toString() : "";

            context.append(String.format("--- %s [%s] ---\n%s\n\n", filePath, chunkType, content));

            if (context.length() > maxContextLength) break;
        }

        String prompt = switch (insightType) {
            case "architecture" -> String.format("""
                Analyze the following code snippets and provide a comprehensive architecture overview.
                Include: main components, design patterns used, technology stack, module structure,
                and how different parts interact. Format with clear sections.

                %s
                """, context);

            case "onboarding" -> String.format("""
                Based on the following code snippets, create a developer onboarding guide.
                Include: project overview, key directories, important files to read first,
                development workflow, and key concepts a new developer needs to understand.

                %s
                """, context);

            case "flow" -> String.format("""
                Trace the %s flow through the codebase based on these code snippets.
                Show the sequence of function calls, data transformations, and control flow.
                Reference specific files and functions.

                %s
                """, additionalContext != null ? additionalContext : "main", context);

            default -> "Provide a summary of this codebase based on the available code.";
        };

        return generateAnswer(prompt, context.toString());
    }
}
