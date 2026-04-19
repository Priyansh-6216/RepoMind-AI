package com.repomind.dto;

import lombok.Data;

/**
 * Request DTO for sending a chat question about a repository.
 */
@Data
public class ChatRequest {

    private String sessionId;

    private String question;
}
