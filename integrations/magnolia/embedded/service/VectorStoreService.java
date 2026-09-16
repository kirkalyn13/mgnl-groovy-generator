package com.sample.cms.embedded.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import okhttp3.*;
import com.sample.cms.embedded.dto.IngestPoint;
import com.sample.cms.embedded.dto.ScoredPoint;

import javax.inject.Inject;
import javax.jcr.RepositoryException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import static com.sample.cms.embedded.util.EmbeddedGroovyGeneratorConstants.*;
import static com.sample.cms.helpers.GroovyGeneratorHelpers.getKeystoreValue;

/**
 * Performs similarity search against a vector store collection
 * Returns matches as {@link ScoredPoint} instances.
 */
public class VectorStoreService {
    private final OkHttpClient client;
    private final ObjectMapper mapper;

    @Inject
    public VectorStoreService(OkHttpClient client) {
        this.client = client;
        this.mapper = new ObjectMapper();
    }

    /**
     * Embeds the given query vector into a vector search similarity search request and returns the
     * top-K matching points with their payloads.
     *
     * @param queryVector Embedding vector to search against the collection.
     * @param topK        Maximum number of matches to return.
     * @return List of {@link ScoredPoint} matches ordered by descending similarity.
     */
    public List<ScoredPoint> search(float[] queryVector, int topK) throws IOException, RepositoryException {
        ObjectNode body = mapper.createObjectNode();
        body.put("limit", topK);
        body.put("with_payload", true);
        ArrayNode vec = body.putArray("vector");
        for (float v : queryVector) vec.add(v);

        Request request = new Request.Builder()
                .url(getKeystoreValue(VECTOR_STORE_URL_PATH) + "/collections/" + getKeystoreValue(COLLECTION_NAME_PATH) + "/points/search")
                .header("api-key", getKeystoreValue(VECTOR_STORE_API_KEY_PATH))
                .post(RequestBody.create(mapper.writeValueAsBytes(body), MediaType.get("application/json")))
                .build();

        try (Response response = client.newCall(request).execute()) {
            JsonNode results = mapper.readTree(response.body().string()).path("result");
            List<ScoredPoint> points = new ArrayList<>();
            results.forEach(r -> points.add(ScoredPoint.fromJson(r)));
            return points;
        }
    }

    /**
     * Embeds each script and upserts it into the vector store collection as a point, deriving a stable
     * point ID from each script's natural key so re-ingesting the same node overwrites its
     * existing point rather than creating a duplicate.
     *
     * @param scripts          Scripts to embed and store, each carrying a natural key (e.g. JCR path).
     * @param embeddingService Service used to embed each script's content.
     */
    public void upsert(List<IngestPoint> scripts, EmbeddingService embeddingService) throws IOException, RepositoryException {
        ArrayNode points = mapper.createArrayNode();

        for (IngestPoint point : scripts) {
            float[] vector = embeddingService.embed(point.script());
            String pointId = UUID.nameUUIDFromBytes(point.id().getBytes(StandardCharsets.UTF_8)).toString();

            ObjectNode vectorStorePoint = points.addObject();
            vectorStorePoint.put("id", pointId);
            ArrayNode vec = vectorStorePoint.putArray("vector");
            for (float v : vector) vec.add(v);
            vectorStorePoint.putObject("payload").put("text", point.script());
        }

        ObjectNode body = mapper.createObjectNode();
        body.set("points", points);

        Request request = new Request.Builder()
                .url(getKeystoreValue(VECTOR_STORE_URL_PATH) + "/collections/" + getKeystoreValue(COLLECTION_NAME_PATH) + "/points")
                .header("api-key", getKeystoreValue(VECTOR_STORE_API_KEY_PATH))
                .put(RequestBody.create(mapper.writeValueAsBytes(body), MediaType.get("application/json")))
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Failed to upsert points: " + response.body().string());
            }
        }
    }
}