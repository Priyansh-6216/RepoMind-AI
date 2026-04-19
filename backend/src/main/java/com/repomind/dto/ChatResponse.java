package com.repomind.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Response DTO for chat Q&A — includes the AI answer and source citations.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {

    private String sessionId;

    private String answer;

    private List<Citation> citations;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Citation {

        private String chunkId;

        private String filePath;

        private String chunkName;

        private String chunkType;

        private Integer startLine;

        private Integer endLine;

        private Double relevanceScore;

        private String snippet;
    }
}
