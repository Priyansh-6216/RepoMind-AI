package com.repomind.repository;

import com.repomind.model.CodeChunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface CodeChunkRepo extends JpaRepository<CodeChunk, UUID> {

    List<CodeChunk> findByRepositoryId(UUID repositoryId);

    long countByRepositoryId(UUID repositoryId);

    List<CodeChunk> findByFileId(UUID fileId);

    /**
     * Perform cosine similarity search against pgvector embeddings.
     * Returns top-K most similar code chunks for a given query embedding.
     *
     * The <=> operator computes cosine distance (1 - cosine_similarity).
     * Lower distance = higher similarity.
     *
     * @param repositoryId Filter chunks to a specific repository
     * @param queryEmbedding The query's embedding vector as a string "[0.1, 0.2, ...]"
     * @param limit Number of results (top-K)
     * @return Ordered list of most similar code chunks
     */
    @Query(value = """
        SELECT c.id, c.file_id, c.repository_id, c.chunk_type, c.name,
               c.content, c.start_line, c.end_line, c.metadata, c.created_at,
               (c.embedding <=> CAST(:queryEmbedding AS vector)) AS distance
        FROM code_chunks c
        WHERE c.repository_id = :repositoryId
        ORDER BY c.embedding <=> CAST(:queryEmbedding AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Object[]> findSimilarChunks(
            @Param("repositoryId") UUID repositoryId,
            @Param("queryEmbedding") String queryEmbedding,
            @Param("limit") int limit
    );

    /**
     * Get a summary of chunk types and counts for a repository.
     */
    @Query(value = """
        SELECT c.chunk_type, COUNT(*) as cnt
        FROM code_chunks c
        WHERE c.repository_id = :repositoryId
        GROUP BY c.chunk_type
        ORDER BY cnt DESC
        """, nativeQuery = true)
    List<Object[]> getChunkTypeSummary(@Param("repositoryId") UUID repositoryId);
}
