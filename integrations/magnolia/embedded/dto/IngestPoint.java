package com.sample.cms.embedded.dto;

/**
 * Carries a script's natural key (e.g. JCR path or identifier) alongside its raw content for
 * embedding and upsert into the vector store.
 *
 * @param id     Natural key identifying the source script (e.g. JCR node path).
 * @param script Raw script content to embed.
 */
public record IngestPoint(String id, String script) {}
