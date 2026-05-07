package com.sample.cms.actions;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import info.magnolia.cms.security.SecurityUtil;
import info.magnolia.context.MgnlContext;
import info.magnolia.jcr.util.PropertyUtil;
import info.magnolia.ui.CloseHandler;
import info.magnolia.ui.ValueContext;
import info.magnolia.ui.api.action.ActionExecutionException;
import info.magnolia.ui.api.message.Message;
import info.magnolia.ui.api.message.MessageType;
import info.magnolia.ui.contentapp.Datasource;
import info.magnolia.ui.contentapp.action.CommitAction;
import info.magnolia.ui.editor.FormView;
import info.magnolia.ui.framework.message.MessagesManager;
import info.magnolia.ui.observation.DatasourceObservation;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.RepositoryException;
import javax.jcr.Session;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;

/**
 * Action that generates a Groovy script based on a user query by calling an external
 * AI-powered groovy generator API, then saves the result as a node in the Magnolia scripts workspace.
 */
public class GenerateScriptAction extends CommitAction<GenerateScriptActionDefinition> {

    private final FormView<GenerateScriptActionDefinition> form;
    private final MessagesManager messages;
    private static final String GROOVY_GENERATOR_PATH = "/groovy-generator/url";
    private static final String API_KEY_PATH = "/groovy-generator/api-key";
    private static final String GENERATE_PATH = "/v1/scripts/generate";
    private static final String GROOVY_WORKSPACE = "scripts";
    private static final String KEYSTORE_WORKSPACE = "keystore";
    private static final String SCRIPT_NODE_TYPE = "mgnl:content";
    private static final String PASSWORD_PROPERTY = "encryptedValue";
    private static final String QUERY_PROPERTY = "query";
    private static final String WORKSPACES_PROPERTY = "workspaces";
    private static final String PROPERTIES_PROPERTY = "properties";
    private static final String FILENAME_PREFIX = "generated-script-";
    private static final Integer REQUEST_TIMEOUT = 120;

    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    /**
     * @param definition            Action definition containing configuration.
     * @param closeHandler          Handles closing the dialog after execution.
     * @param valueContext          Provides the current JCR node context.
     * @param form                  The dialog form view to read field values from.
     * @param datasource            Datasource bound to the content app.
     * @param datasourceObservation Triggers UI refresh after datasource changes.
     * @param messages              Sends notifications to the Magnolia message bar.
     */
    @Inject
    public GenerateScriptAction(
            GenerateScriptActionDefinition definition,
            CloseHandler closeHandler,
            ValueContext<GenerateScriptActionDefinition> valueContext,
            FormView<GenerateScriptActionDefinition> form,
            Datasource<GenerateScriptActionDefinition> datasource,
            DatasourceObservation.Manual datasourceObservation,
            MessagesManager messages) {
        super(definition, closeHandler, valueContext, form, datasource, datasourceObservation);
        this.form = form;
        this.messages = messages;
    }

    /**
     * Validates the form, reads query, workspaces, and properties, calls the generator API,
     * saves the resulting script, and notifies the user on success.
     */
    @Override
    public void execute() throws ActionExecutionException {
        if (!super.validateForm()) return;
        super.execute();

        try {
            String query = form.getPropertyValue(QUERY_PROPERTY).orElseThrow().toString();
            List<String> workspaces = form.getPropertyValue(WORKSPACES_PROPERTY).stream().map(Object::toString).toList();
            List<String> properties = form.getPropertyValue(PROPERTIES_PROPERTY).stream().map(Object::toString).toList();
            Boolean allowModifications = ((GenerateScriptActionDefinition) this.getDefinition()).getAllowModifications();

            GenerateResponse response = sendGenerateRequest(query, workspaces, properties, allowModifications);
            saveGeneratedScript(response.script());
            String resultMessage = String.format("Successfully Generated Script: \n %s", response.script());
            messages.sendLocalMessage(new Message(MessageType.INFO, "Script Generated", resultMessage));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Sends a POST request to the generator API with the query, workspace, and properties.
     *
     * @param query      Natural language query describing the desired script.
     * @param workspaces List of JCR workspace name to scope the script to.
     * @param properties List of JCR property names relevant to the query.
     * @param allowModifications boolean to specify if modification script requests are allowed.
     * @return Parsed {@link GenerateResponse} from the API.
     */
    private GenerateResponse sendGenerateRequest(String query, List<String> workspaces, List<String> properties, Boolean allowModifications) throws IOException, InterruptedException, RepositoryException {
        GenerateRequest requestBody = new GenerateRequest(query, workspaces, properties, allowModifications);
        String body = new ObjectMapper().writeValueAsString(requestBody);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(getGeneratorUrl()))
                .header("Content-Type", "application/json")
                .header("X-API-Key", getKeystoreValue(API_KEY_PATH))
                .timeout(Duration.ofSeconds(REQUEST_TIMEOUT))
                .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                .build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new IOException("Unexpected response status: " + response.statusCode() + " — " + response.body());
        }

        return mapGenerateResponse(response.body());
    }

    /**
     * Maps the raw JSON response body to a {@link GenerateResponse} record.
     *
     * @param response Raw JSON string from the generator API.
     * @return Parsed {@link GenerateResponse}.
     */
    private static GenerateResponse mapGenerateResponse(String response) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(response);

        return new GenerateResponse(
                root.path("success").asBoolean(),
                root.path("query").asText(),
                root.path("script").asText(),
                root.path("retries").asInt());
    }

    /**
     * Saves the generated script as a {@code mgnl:content} node in the scripts workspace.
     * Node is named with a timestamp prefix to ensure uniqueness.
     *
     * @param code The generated Groovy script content.
     */
    private void saveGeneratedScript(String code) throws RepositoryException {
        Session session = MgnlContext.getJCRSession(GROOVY_WORKSPACE);
        String nodeName = FILENAME_PREFIX + System.currentTimeMillis();

        Node rootNode = session.getRootNode();
        Node scriptNode = rootNode.addNode(nodeName, SCRIPT_NODE_TYPE);
        scriptNode.setProperty("script", true);
        scriptNode.setProperty("text", code);

        session.save();
    }

    /**
     * Retrieves and decrypts the groovy generator keystore values.
     *
     * @return the decrypted keystore value
     */
    private static String getKeystoreValue(String path) throws RepositoryException {
        Session session = MgnlContext.getJCRSession(KEYSTORE_WORKSPACE);
        Node tokenNode = session.getNode(path);
        String encryptedToken = PropertyUtil.getString(tokenNode, PASSWORD_PROPERTY);

        return SecurityUtil.decrypt(encryptedToken);
    }

    /**
     * Retrieves the generator API URL from keystore then appends generate path
     *
     * @return Generator URL string.
     */
    private String getGeneratorUrl() throws RepositoryException {
        return getKeystoreValue(GROOVY_GENERATOR_PATH) + GENERATE_PATH;
    }

    /** Request payload sent to the generator API. */
    @JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
    private record GenerateRequest(String query, List<String> workspaces, List<String> properties, Boolean allowModifications) {}

    /** Response payload received from the generator API. */
    private record GenerateResponse(boolean success, String query, String script, int retries) {}
}