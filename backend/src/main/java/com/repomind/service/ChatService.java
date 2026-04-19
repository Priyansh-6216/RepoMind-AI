package com.repomind.service;

import com.repomind.dto.ChatRequest;
import com.repomind.dto.ChatResponse;
import com.repomind.model.ChatMessage;
import com.repomind.model.ChatSession;
import com.repomind.repository.ChatMessageRepo;
import com.repomind.repository.ChatSessionRepo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Chat service — manages sessions and messages, delegates Q&A to RAGService.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ChatService {

    private final ChatSessionRepo chatSessionRepo;
    private final ChatMessageRepo chatMessageRepo;
    private final RAGService ragService;

    /**
     * Process a chat question — creates/reuses session, runs RAG, stores messages.
     */
    @Transactional
    public ChatResponse processChat(UUID repoId, ChatRequest request) {
        // Get or create session
        ChatSession session;

        if (request.getSessionId() != null && !request.getSessionId().isBlank()) {
            session = chatSessionRepo.findById(UUID.fromString(request.getSessionId()))
                    .orElseThrow(() -> new RuntimeException("Session not found"));
        } else {
            // Create new session with a title derived from the question
            String title = request.getQuestion().length() > 60
                    ? request.getQuestion().substring(0, 60) + "..."
                    : request.getQuestion();

            session = ChatSession.builder()
                    .repositoryId(repoId)
                    .title(title)
                    .build();
            session = chatSessionRepo.save(session);
            log.info("Created new chat session: {}", session.getId());
        }

        // Save user message
        ChatMessage userMessage = ChatMessage.builder()
                .sessionId(session.getId())
                .role("USER")
                .content(request.getQuestion())
                .build();
        chatMessageRepo.save(userMessage);

        // Run RAG pipeline
        ChatResponse.ChatResponseBuilder responseBuilder = ragService.processQuestion(
                repoId, request.getQuestion()
        );

        ChatResponse response = responseBuilder
                .sessionId(session.getId().toString())
                .build();

        // Save assistant message with citations
        List<Map<String, Object>> citationMaps = response.getCitations() != null
                ? response.getCitations().stream()
                    .map(c -> {
                        Map<String, Object> map = new HashMap<>();
                        map.put("file_path", c.getFilePath());
                        map.put("chunk_id", c.getChunkId());
                        map.put("chunk_name", c.getChunkName());
                        map.put("start_line", c.getStartLine());
                        map.put("end_line", c.getEndLine());
                        map.put("relevance_score", c.getRelevanceScore());
                        return map;
                    })
                    .collect(Collectors.toList())
                : List.of();

        ChatMessage assistantMessage = ChatMessage.builder()
                .sessionId(session.getId())
                .role("ASSISTANT")
                .content(response.getAnswer())
                .citations(citationMaps)
                .build();
        chatMessageRepo.save(assistantMessage);

        // Update session timestamp
        session.setUpdatedAt(java.time.Instant.now());
        chatSessionRepo.save(session);

        return response;
    }

    /**
     * Get all chat sessions for a repository.
     */
    public List<ChatSession> getSessions(UUID repoId) {
        return chatSessionRepo.findByRepositoryIdOrderByUpdatedAtDesc(repoId);
    }

    /**
     * Get all messages for a specific session.
     */
    public List<ChatMessage> getSessionMessages(UUID sessionId) {
        return chatMessageRepo.findBySessionIdOrderByCreatedAtAsc(sessionId);
    }
}
