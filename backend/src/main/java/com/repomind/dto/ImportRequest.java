package com.repomind.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * Request DTO for importing a GitHub repository.
 */
@Data
public class ImportRequest {

    @NotBlank(message = "Repository URL is required")
    @Pattern(
        regexp = "^https://github\\.com/[\\w.-]+/[\\w.-]+/?$",
        message = "Must be a valid GitHub URL (https://github.com/owner/repo)"
    )
    private String url;
}
