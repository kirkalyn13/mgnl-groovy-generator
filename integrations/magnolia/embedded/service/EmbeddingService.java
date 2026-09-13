package com.sample.cms.embedded.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import okhttp3.*;

import javax.inject.Inject;
import javax.jcr.RepositoryException;
import java.io.IOException;

import static com.sample.cms.embedded.util.EmbeddedGroovyGeneratorConstants.*;
import static com.sample.cms.helpers.GroovyGeneratorHelpers.getKeystoreValue;

public class EmbeddingService {
    private final ObjectMapper mapper;

    private final OkHttpClient client = HttpClientFactory.newInstance();
    private static final MediaType MEDIA_TYPE = MediaType.get("application/json");

    @Inject
    public EmbeddingService() {
        this.mapper = new ObjectMapper();
    }

    /**
     * Sends the given text to LLM's embedding endpoint and converts the returned vector
     * into a float array.
     *
     * @param text Text to generate an embedding for.
     * @return The embedding vector as a float array.
     */
    public float[] embed(String text) throws JsonProcessingException, RepositoryException {
        ObjectNode body = mapper.createObjectNode();
        body.putObject("content").putArray("parts").addObject().put("text", text);

        Request request = new Request.Builder()
                .url(getKeystoreValue(EMBED_ENDPOINT_PATH) + "?key=" + getKeystoreValue(LLM_API_KEY_PATH))
                .post(RequestBody.create(mapper.writeValueAsBytes(body), MEDIA_TYPE))
                .build();

        try (Response response = client.newCall(request).execute()) {
            JsonNode values = mapper.readTree(response.body().string()).path("embedding").path("values");
            float[] result = new float[values.size()];
            for (int i = 0; i < values.size(); i++) result[i] = (float) values.get(i).asDouble();
            return result;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Sends the given prompt to LLM's Interactions API and extracts the model's raw text
     * output from the response's {@code steps} array.
     *
     * @param prompt Fully assembled prompt to send to the LLM.
     * @return The raw text content of the model's output step.
     * @throws IOException If the LLM returns an error, or no {@code model_output} step is present.
     */
    public String generate(String prompt) throws IOException, RepositoryException {
        ObjectNode body = mapper.createObjectNode();
        body.put("model", getKeystoreValue(GENERATE_MODEL_PATH));
        body.put("input", prompt);

        Request request = new Request.Builder()
                .url(getKeystoreValue(GENERATE_ENDPOINT_PATH))
                .header("x-goog-api-key", getKeystoreValue(LLM_API_KEY_PATH))
                .post(RequestBody.create(mapper.writeValueAsBytes(body), MEDIA_TYPE))
                .build();

        try (Response response = client.newCall(request).execute()) {
            String raw = response.body().string();
            JsonNode json = mapper.readTree(raw);

            if (json.has("error")) {
                throw new IOException("LLM Error: " + json.path("error").path("message").asText());
            }

            for (JsonNode step : json.path("steps")) {
                if ("model_output".equals(step.path("type").asText())) {
                    return step.path("content").get(0).path("text").asText();
                }
            }

            throw new IOException("No model_output step in LLM response: " + raw);
        }
    }
}
