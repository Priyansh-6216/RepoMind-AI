package com.repomind.controller;

import com.repomind.dto.ImportRequest;
import com.repomind.model.Repository;
import com.repomind.service.RepoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * REST controller for repository management.
 *
 * Endpoints:
 *   POST   /repos/import     — Import a GitHub repo
 *   GET    /repos             — List all repos
 *   GET    /repos/{id}        — Get repo details
 *   GET    /repos/{id}/status — Get indexing status
 *   DELETE /repos/{id}        — Delete repo
 */
@RestController
@RequestMapping("/repos")
@RequiredArgsConstructor
public class RepoController {

    private final RepoService repoService;

    @PostMapping("/import")
    public ResponseEntity<Map<String, Object>> importRepo(@Valid @RequestBody ImportRequest request) {
        Map<String, Object> result = repoService.importRepository(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    @GetMapping
    public ResponseEntity<List<Repository>> listRepos() {
        return ResponseEntity.ok(repoService.getAllRepositories());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Repository> getRepo(@PathVariable UUID id) {
        return ResponseEntity.ok(repoService.getRepository(id));
    }

    @GetMapping("/{id}/status")
    public ResponseEntity<Map<String, Object>> getStatus(@PathVariable UUID id) {
        return ResponseEntity.ok(repoService.getRepositoryStatus(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRepo(@PathVariable UUID id) {
        repoService.deleteRepository(id);
        return ResponseEntity.noContent().build();
    }
}
