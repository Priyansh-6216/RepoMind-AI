package com.repomind.controller;

import com.repomind.dto.ChatRequest;
import com.repomind.dto.ChatResponse;
import com.repomind.model.ChatMessage;
import com.repomind.model.ChatSession;
import com.repomind.service.ChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * REST controller for AI-powered chat Q&A over repository codebases.
 *
 * Endpoints:
 *   POST /repos/{id}/chat                — Ask a question
 *   GET  /repos/{id}/chat/sessions       — List chat sessions
 *   GET  /repos/{id}/chat/sessions/{sid} — Get session messages
 */
@RestController
@RequestMapping("/repos/{repoId}/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @PostMapping
    public ResponseEntity<ChatResponse> askQuestion(
            @PathVariable UUID repoId,
            @jakarta.validation.Valid @RequestBody ChatRequest request) {

        ChatResponse response = chatService.processChat(repoId, request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/sessions")
    public ResponseEntity<List<ChatSession>> listSessions(@PathVariable UUID repoId) {
        return ResponseEntity.ok(chatService.getSessions(repoId));
    }

    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<List<ChatMessage>> getSessionMessages(
            @PathVariable UUID repoId,
            @PathVariable UUID sessionId) {

        return ResponseEntity.ok(chatService.getSessionMessages(sessionId));
    }
}
