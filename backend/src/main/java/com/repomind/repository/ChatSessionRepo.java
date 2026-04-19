package com.repomind.repository;

import com.repomind.model.ChatSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ChatSessionRepo extends JpaRepository<ChatSession, UUID> {

    List<ChatSession> findByRepositoryIdOrderByUpdatedAtDesc(UUID repositoryId);
}
