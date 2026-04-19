package com.repomind;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * RepoMind AI — Main Application Entry Point
 *
 * AI-powered code intelligence platform enabling semantic search
 * and grounded Q&A over GitHub repositories using RAG.
 */
@SpringBootApplication
public class RepoMindApplication {

    public static void main(String[] args) {
        SpringApplication.run(RepoMindApplication.class, args);
    }
}
