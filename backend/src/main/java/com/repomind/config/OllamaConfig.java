package com.repomind.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

/**
 * Ollama local LLM configuration.
 * Provides a WebClient configured for Ollama API calls.
 */
@Configuration
@ConfigurationProperties(prefix = "ollama")
@Getter @Setter
public class OllamaConfig {

    private String baseUrl = "http://localhost:11434";
    private String chatModel = "llama3.1";
    private String embedModel = "nomic-embed-text";
    private int embeddingDim = 768;

    @Bean
    public WebClient ollamaWebClient() {
        return WebClient.builder()
                .baseUrl(baseUrl)
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
    }
}
