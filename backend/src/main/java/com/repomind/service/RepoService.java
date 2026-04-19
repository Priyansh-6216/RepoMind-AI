package com.repomind.service;

import com.repomind.dto.ImportRequest;
import com.repomind.model.IndexJob;
import com.repomind.model.Repository;
import com.repomind.repository.IndexJobRepo;
import com.repomind.repository.RepositoryRepo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service layer for repository management — import, status, listing.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class RepoService {

    private final RepositoryRepo repositoryRepo;
    private final IndexJobRepo indexJobRepo;
    private final JobPublisherService jobPublisherService;

    /**
     * Import a GitHub repository for indexing.
     * Creates the repository record, an index job, and publishes to Redis.
     */
    @Transactional
    public Map<String, Object> importRepository(ImportRequest request) {
        String url = request.getUrl().replaceAll("/$", "");

        // Check for duplicate
        if (repositoryRepo.existsByUrl(url)) {
            Repository existing = repositoryRepo.findByUrl(url).orElseThrow();

            // Allow re-indexing if previously failed
            if (!"FAILED".equals(existing.getStatus())) {
                return Map.of(
                    "id", existing.getId(),
                    "name", existing.getName(),
                    "owner", existing.getOwner(),
                    "status", existing.getStatus(),
                    "message", "Repository already imported"
                );
            }

            // Reset for re-indexing
            existing.setStatus("PENDING");
            repositoryRepo.save(existing);
            return createAndPublishJob(existing);
        }

        // Parse owner/name from URL
        String[] parts = url.split("/");
        String owner = parts[parts.length - 2];
        String name = parts[parts.length - 1];

        // Create repository record
        Repository repo = Repository.builder()
                .url(url)
                .name(name)
                .owner(owner)
                .status("PENDING")
                .build();

        repo = repositoryRepo.save(repo);
        log.info("Repository created: {} ({})", repo.getName(), repo.getId());

        return createAndPublishJob(repo);
    }

    private Map<String, Object> createAndPublishJob(Repository repo) {
        // Create index job
        IndexJob job = IndexJob.builder()
                .repositoryId(repo.getId())
                .status("QUEUED")
                .build();

        job = indexJobRepo.save(job);
        log.info("Index job created: {}", job.getId());

        // Publish to Redis queue
        jobPublisherService.publishIndexJob(job.getId(), repo.getId());

        return Map.of(
            "id", repo.getId(),
            "name", repo.getName(),
            "owner", repo.getOwner(),
            "status", repo.getStatus(),
            "jobId", job.getId()
        );
    }

    /**
     * Get all repositories ordered by creation date.
     */
    public List<Repository> getAllRepositories() {
        return repositoryRepo.findAllByOrderByCreatedAtDesc();
    }

    /**
     * Get a single repository by ID.
     */
    public Repository getRepository(UUID id) {
        return repositoryRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Repository not found: " + id));
    }

    /**
     * Get the current indexing status for a repository.
     */
    public Map<String, Object> getRepositoryStatus(UUID repoId) {
        Repository repo = getRepository(repoId);
        IndexJob latestJob = indexJobRepo.findTopByRepositoryIdOrderByCreatedAtDesc(repoId)
                .orElse(null);

        Map<String, Object> status = new java.util.HashMap<>(Map.of(
            "repoId", repo.getId(),
            "repoStatus", repo.getStatus(),
            "fileCount", repo.getFileCount(),
            "chunkCount", repo.getChunkCount()
        ));

        if (latestJob != null) {
            status.put("jobId", latestJob.getId());
            status.put("jobStatus", latestJob.getStatus());
            status.put("progress", latestJob.getProgress());
            status.put("totalFiles", latestJob.getTotalFiles());
            status.put("processedFiles", latestJob.getProcessedFiles());
            if (latestJob.getErrorMessage() != null) {
                status.put("errorMessage", latestJob.getErrorMessage());
            }
        }

        return status;
    }

    /**
     * Delete a repository and all associated data (cascades via FK).
     */
    @Transactional
    public void deleteRepository(UUID id) {
        Repository repo = getRepository(id);
        repositoryRepo.delete(repo);
        log.info("Repository deleted: {} ({})", repo.getName(), id);
    }
}
