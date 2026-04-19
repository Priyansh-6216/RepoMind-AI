package com.repomind.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for insight generation (architecture, onboarding, flow tracing).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InsightResponse {

    private String type;

    private String title;

    private String content;

    private List<String> keyPoints;

    private List<ChatResponse.Citation> relatedFiles;

    private Map<String, Object> metadata;
}
