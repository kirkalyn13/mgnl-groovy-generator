package com.sample.cms.embedded.util;

/**
 * Constants for the Magnolia-native (embedded) Groovy generator, including vector search
 * defaults and keystore node paths for the LLM and vector store configuration.
 */
public class EmbeddedGroovyGeneratorConstants {
    private EmbeddedGroovyGeneratorConstants() {}

    // Vector Store Config
    public static final int TOP_K = 5;

    // Keystore
    private static final String ROOT_PATH = "/groovy-generator/embedded";
    private static final String LLM_PATH = ROOT_PATH + "/llm";
    private static final String VECTOR_STORE_PATH = ROOT_PATH + "/vector-store";

    public static final String EMBED_ENDPOINT_PATH = LLM_PATH + "/embed-endpoint";
    public static final String GENERATE_ENDPOINT_PATH = LLM_PATH + "/generate-endpoint";
    public static final String GENERATE_MODEL_PATH = LLM_PATH + "/model";
    public static final String LLM_API_KEY_PATH = LLM_PATH + "/api-key";
    public static final String VECTOR_STORE_URL_PATH = VECTOR_STORE_PATH + "/url";
    public static final String VECTOR_STORE_API_KEY_PATH = VECTOR_STORE_PATH + "/api-key";
    public static final String COLLECTION_NAME_PATH = VECTOR_STORE_PATH + "/collection-name";
}
