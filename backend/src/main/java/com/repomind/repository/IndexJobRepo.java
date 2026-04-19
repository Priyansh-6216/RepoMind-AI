package com.repomind.repository;

import com.repomind.model.IndexJob;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface IndexJobRepo extends JpaRepository<IndexJob, UUID> {

    List<IndexJob> findByRepositoryIdOrderByCreatedAtDesc(UUID repositoryId);

    Optional<IndexJob> findTopByRepositoryIdOrderByCreatedAtDesc(UUID repositoryId);
}
