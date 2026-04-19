package com.repomind.model;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

/**
 * Represents a semantic code chunk with its vector embedding.
 * Chunks are created by AST-based parsing (functions, classes, methods).
 * Embeddings are 768-dimensional vectors from Ollama nomic-embed-text.
 */
@Entity
@Table(name = "code_chunks")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class CodeChunk {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "file_id", nullable = false)
    private UUID fileId;

    @Column(name = "repository_id", nullable = false)
    private UUID repositoryId;

    @Column(name = "chunk_type", nullable = false)
    private String chunkType;

    private String name;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "start_line")
    private Integer startLine;

    @Column(name = "end_line")
    private Integer endLine;

    /**
     * Vector embedding is handled via native queries for pgvector operations.
     * JPA does not natively support the vector type, so similarity searches
     * use native SQL with the <=> cosine distance operator.
     */

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> metadata;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;
}
