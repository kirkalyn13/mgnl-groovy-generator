package com.sample.cms.embedded.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import okhttp3.*;

import javax.inject.Inject;
import javax.jcr.RepositoryException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static com.sample.cms.embedded.util.EmbeddedGroovyGeneratorConstants.*;
import static com.sample.cms.helpers.GroovyGeneratorHelpers.getKeystoreValue;

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
}