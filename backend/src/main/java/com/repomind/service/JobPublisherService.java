package com.repomind.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

/**
 * Publishes indexing jobs to the Redis queue for the Python worker to consume.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class JobPublisherService {

    private static final String JOB_QUEUE = "repomind:index_jobs";

    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;

    /**
     * Publish an indexing job to the Redis queue.
     *
     * @param jobId The UUID of the created IndexJob
     * @param repositoryId The UUID of the repository to index
     */
    public void publishIndexJob(UUID jobId, UUID repositoryId) {
        try {
            Map<String, String> jobPayload = Map.of(
                "job_id", jobId.toString(),
                "repository_id", repositoryId.toString()
            );

            String json = objectMapper.writeValueAsString(jobPayload);
            redisTemplate.opsForList().leftPush(JOB_QUEUE, json);

            log.info("Published indexing job to Redis queue: jobId={}, repoId={}", jobId, repositoryId);

        } catch (Exception e) {
            log.error("Failed to publish job to Redis: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to queue indexing job", e);
        }
    }
}
