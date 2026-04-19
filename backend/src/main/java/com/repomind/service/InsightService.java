package com.repomind.service;

import com.repomind.dto.ChatResponse;
import com.repomind.dto.InsightResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Insight generation service — architecture summaries, onboarding guides, flow tracing.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class InsightService {

    private final RAGService ragService;

    /**
     * Generate an architecture overview of the repository.
     */
    public InsightResponse generateArchitectureInsight(UUID repoId) {
        log.info("Generating architecture insight for repo: {}", repoId);

        String content = ragService.generateInsight(repoId, "architecture", null);

        return InsightResponse.builder()
                .type("architecture")
                .title("Architecture Overview")
                .content(content)
                .keyPoints(extractKeyPoints(content))
                .metadata(Map.of("repoId", repoId.toString()))
                .build();
    }

    /**
     * Generate an onboarding guide for new developers.
     */
    public InsightResponse generateOnboardingInsight(UUID repoId) {
        log.info("Generating onboarding insight for repo: {}", repoId);

        String content = ragService.generateInsight(repoId, "onboarding", null);

        return InsightResponse.builder()
                .type("onboarding")
                .title("Developer Onboarding Guide")
                .content(content)
                .keyPoints(extractKeyPoints(content))
                .metadata(Map.of("repoId", repoId.toString()))
                .build();
    }

    /**
     * Trace a specific flow through the codebase.
     */
    public InsightResponse traceFlow(UUID repoId, String flowName) {
        log.info("Tracing flow '{}' for repo: {}", flowName, repoId);

        String content = ragService.generateInsight(repoId, "flow", flowName);

        return InsightResponse.builder()
                .type("flow")
                .title("Flow Trace: " + flowName)
                .content(content)
                .keyPoints(extractKeyPoints(content))
                .metadata(Map.of(
                    "repoId", repoId.toString(),
                    "flowName", flowName
                ))
                .build();
    }

    /**
     * Extract key points from generated content by looking for bullet points or numbered items.
     */
    private List<String> extractKeyPoints(String content) {
        if (content == null || content.isBlank()) {
            return List.of();
        }

        return content.lines()
                .filter(line -> line.trim().matches("^[-*•\\d].*"))
                .map(line -> line.trim().replaceFirst("^[-*•]\\s*", "").replaceFirst("^\\d+\\.?\\s*", ""))
                .filter(line -> !line.isBlank())
                .limit(10)
                .toList();
    }
}
