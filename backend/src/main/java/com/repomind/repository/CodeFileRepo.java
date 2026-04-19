package com.repomind.repository;

import com.repomind.model.CodeFile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface CodeFileRepo extends JpaRepository<CodeFile, UUID> {

    List<CodeFile> findByRepositoryId(UUID repositoryId);

    long countByRepositoryId(UUID repositoryId);

    List<CodeFile> findByRepositoryIdAndLanguage(UUID repositoryId, String language);
}
