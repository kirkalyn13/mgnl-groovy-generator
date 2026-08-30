package com.sample.cms.constants;

public final class GroovyGeneratorConstants {

    private GroovyGeneratorConstants() {}

    // Keystore
    public static final String GROOVY_GENERATOR_PATH = "/groovy-generator/url";
    public static final String API_KEY_PATH = "/groovy-generator/api-key";
    public static final String KEYSTORE_WORKSPACE = "keystore";
    public static final String PASSWORD_PROPERTY = "encryptedValue";

    // API paths
    public static final String GENERATE_PATH = "/v1/scripts/generate";
    public static final String REVIEW_PATH = "/v1/scripts/review";

    // Scripts workspace
    public static final String GROOVY_WORKSPACE = "scripts";
    public static final String SCRIPT_NODE_TYPE = "mgnl:content";
    public static final String FILENAME_PREFIX = "generated-script-";

    // Form properties
    public static final String QUERY_PROPERTY = "query";
    public static final String WORKSPACES_PROPERTY = "workspaces";
    public static final String PROPERTIES_PROPERTY = "properties";
    public static final String QUERY_PREFIX = "Groovy script request";

    // Misc
    public static final Integer REQUEST_TIMEOUT = 120;
}
