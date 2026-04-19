package com.repomind.model;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.Instant;
import java.util.UUID;

/**
 * Represents an indexing pipeline job for a repository.
 * Tracks progress through QUEUED → CLONING → PARSING → EMBEDDING → COMPLETED | FAILED.
 */
@Entity
@Table(name = "index_jobs")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class IndexJob {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "repository_id", nullable = false)
    private UUID repositoryId;

    @Column(nullable = false)
    @Builder.Default
    private String status = "QUEUED";

    @Builder.Default
    private Integer progress = 0;

    @Column(name = "total_files")
    @Builder.Default
    private Integer totalFiles = 0;

    @Column(name = "processed_files")
    @Builder.Default
    private Integer processedFiles = 0;

    @Column(name = "error_message")
    private String errorMessage;

    @Column(name = "started_at")
    private Instant startedAt;

    @Column(name = "completed_at")
    private Instant completedAt;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;
}
