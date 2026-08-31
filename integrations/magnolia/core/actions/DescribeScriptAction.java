package com.sample.cms.actions;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import info.magnolia.cms.security.SecurityUtil;
import info.magnolia.context.MgnlContext;
import info.magnolia.jcr.util.PropertyUtil;
import info.magnolia.ui.api.action.AbstractAction;
import info.magnolia.ui.api.action.ActionExecutionException;
import info.magnolia.ui.api.message.Message;
import info.magnolia.ui.api.message.MessageType;
import info.magnolia.ui.framework.message.MessagesManager;
import info.magnolia.ui.vaadin.integration.jcr.AbstractJcrNodeAdapter;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.RepositoryException;
import javax.jcr.Session;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import static sanofi.campus.constants.GroovyGeneratorConstants.*;

/**
 * Action that sends the selected Groovy script node to the AI generator API for description generation
 * and displays the result as a Magnolia message bar notification.
 */
public class DescribeScriptAction extends AbstractAction<DescribeScriptActionDefinition> {

    private final AbstractJcrNodeAdapter nodeToDescribe;
    private final MessagesManager messages;

    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    /**
     * @param definition    Action definition containing configuration.
     * @param nodeToDescribe  The selected JCR node adapter representing the script to describe.
     * @param messages      Sends notifications to the Magnolia message bar.
     */
    @Inject
    protected DescribeScriptAction(
            DescribeScriptActionDefinition definition,
            AbstractJcrNodeAdapter nodeToDescribe,
            MessagesManager messages) {
        super(definition);
        this.nodeToDescribe = nodeToDescribe;
        this.messages = messages;
    }

    /**
     * Resolves the selected node path, calls the describe API, and displays the result
     * as an info notification in the Magnolia message bar.
     */
    @Override
    public void execute() throws ActionExecutionException {
        try {
            Node node = this.nodeToDescribe.getJcrItem();
            String path = node.getPath();
            String description = sendDescribeRequest(path).description();
            messages.sendLocalMessage(
                    new Message(
                            MessageType.INFO,
                            String.format("Script Description for %s", path),
                            description));
        } catch (RuntimeException | RepositoryException | IOException | InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Sends a GET request to the describe API for the given script path.
     *
     * @param path JCR path of the script node.
     * @return Parsed {@link DescribeResponse} from the API.
     */
    private DescribeResponse sendDescribeRequest(String path) throws IOException, InterruptedException, RepositoryException {
        HttpRequest request = HttpRequest.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .uri(URI.create(getDescribeUrl(path)))
                .header("Content-Type", "application/json")
                .header("X-API-Key", getKeystoreValue(API_KEY_PATH))
                .timeout(Duration.ofSeconds(REQUEST_TIMEOUT))
                .GET().build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new IOException("Unexpected response status: " + response.statusCode() + " — " + response.body());
        }

        return mapDescribeResponse(response.body());
    }

    /**
     * Maps the raw JSON response body to a {@link DescribeResponse} record.
     *
     * @param response Raw JSON string from the describe API.
     * @return Parsed {@link DescribeResponse}.
     */
    private static DescribeResponse mapDescribeResponse(String response) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(response);

        return new DescribeResponse(
                root.path("success").asBoolean(),
                root.path("path").asText(),
                root.path("description").asText());
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
     * Builds the full describe API URL for the given script path.
     *
     * @param path JCR path of the script node.
     * @return Full URL string for the describe endpoint.
     */
    private String getDescribeUrl(String path) throws RepositoryException {
        return String.format("%s%s%s", getKeystoreValue(GROOVY_GENERATOR_PATH), DESCRIBE_PATH, path);
    }

    /** Response payload received from the describe API. */
    private record DescribeResponse(boolean success, String path, String description) {}
}