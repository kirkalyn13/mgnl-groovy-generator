package com.sample.cms.embedded.util;

public class EmbeddedGroovyGeneratorConstants {
    private EmbeddedGroovyGeneratorConstants() {}

    // Vector Store Config
    public static final int TOP_K = 5;

    // Keystore
    public static final String EMBED_ENDPOINT_PATH = "/groovy-generator/embedded/llm/embed-endpoint";
    public static final String GENERATE_ENDPOINT_PATH = "/groovy-generator/embedded/llm/generate-endpoint";
    public static final String GENERATE_MODEL_PATH = "/groovy-generator/embedded/llm/model";
    public static final String LLM_API_KEY_PATH = "/groovy-generator/embedded/llm/api-key";
    public static final String VECTOR_STORE_URL_PATH = "/groovy-generator/embedded/vector-store/url";
    public static final String VECTOR_STORE_API_KEY_PATH = "/groovy-generator/embedded/vector-store/api-key";
    public static final String COLLECTION_NAME_PATH = "/groovy-generator/embedded/vector-store/collection-name";
}
