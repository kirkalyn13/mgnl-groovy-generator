package com.sample.cms.embedded.dto;

import com.fasterxml.jackson.databind.JsonNode;

import java.util.HashMap;
import java.util.Map;

/**
 * A single similarity search result returned by the vector store, holding the matched point's ID,
 * relevance score, and stored payload.
 */
public record ScoredPoint(String id, float score, Map<String, Object> payload) {
    /**
     * Parses a single vector store search result node into a {@link ScoredPoint}, extracting the
     * point ID, similarity score, and payload fields as strings.
     *
     * @param node JSON node representing one entry from vector store's search response.
     * @return The parsed {@link ScoredPoint}.
     */
    public static ScoredPoint fromJson(JsonNode node) {
        Map<String, Object> payload = new HashMap<>();
        node.path("payload").fields().forEachRemaining(e -> payload.put(e.getKey(), e.getValue().asText()));
        return new ScoredPoint(node.path("id").asText(), (float) node.path("score").asDouble(), payload);
    }
}