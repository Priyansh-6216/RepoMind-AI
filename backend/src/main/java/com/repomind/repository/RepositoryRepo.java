package com.repomind.repository;

import com.repomind.model.Repository;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Spring Data JPA repository for GitHub repository records.
 */
@org.springframework.stereotype.Repository
public interface RepositoryRepo extends JpaRepository<Repository, UUID> {

    Optional<Repository> findByUrl(String url);

    boolean existsByUrl(String url);

    List<Repository> findAllByOrderByCreatedAtDesc();

    List<Repository> findByStatus(String status);
}
