package com.repomind.controller;

import com.repomind.dto.InsightResponse;
import com.repomind.service.InsightService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

/**
 * REST controller for AI-powered codebase insights.
 *
 * Endpoints:
 *   POST /repos/{id}/insights/architecture — Architecture overview
 *   POST /repos/{id}/insights/onboarding   — Onboarding guide
 *   POST /repos/{id}/insights/flow         — Flow tracing
 */
@RestController
@RequestMapping("/repos/{repoId}/insights")
@RequiredArgsConstructor
public class InsightController {

    private final InsightService insightService;

    @PostMapping("/architecture")
    public ResponseEntity<InsightResponse> architectureOverview(@PathVariable UUID repoId) {
        return ResponseEntity.ok(insightService.generateArchitectureInsight(repoId));
    }

    @PostMapping("/onboarding")
    public ResponseEntity<InsightResponse> onboardingGuide(@PathVariable UUID repoId) {
        return ResponseEntity.ok(insightService.generateOnboardingInsight(repoId));
    }

    @PostMapping("/flow")
    public ResponseEntity<InsightResponse> traceFlow(
            @PathVariable UUID repoId,
            @RequestBody Map<String, String> request) {

        String flowName = request.getOrDefault("flowName", "main");
        return ResponseEntity.ok(insightService.traceFlow(repoId, flowName));
    }
}
