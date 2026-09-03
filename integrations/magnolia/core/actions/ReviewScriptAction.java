package com.sample.cms.actions;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import info.magnolia.ui.api.action.AbstractAction;
import info.magnolia.ui.api.action.ActionExecutionException;
import info.magnolia.ui.api.message.Message;
import info.magnolia.ui.api.message.MessageType;
import info.magnolia.ui.framework.message.MessagesManager;
import info.magnolia.ui.vaadin.integration.jcr.AbstractJcrNodeAdapter;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.RepositoryException;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import static com.sample.cms.constants.GroovyGeneratorConstants.*;
import static com.sample.cms.helpers.GroovyGeneratorHelpers.getGroovyGeneratorUrl;
import static com.sample.cms.helpers.GroovyGeneratorHelpers.getKeystoreValue;

/**
 * Action that sends the selected Groovy script node to the AI generator API for review
 * and displays the result as a Magnolia message bar notification.
 */
public class ReviewScriptAction extends AbstractAction<ReviewScriptActionDefinition> {

    private final AbstractJcrNodeAdapter nodeToReview;
    private final MessagesManager messages;

    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    /**
     * @param definition    Action definition containing configuration.
     * @param nodeToReview  The selected JCR node adapter representing the script to review.
     * @param messages      Sends notifications to the Magnolia message bar.
     */
    @Inject
    protected ReviewScriptAction(
            ReviewScriptActionDefinition definition,
            AbstractJcrNodeAdapter nodeToReview,
            MessagesManager messages) {
        super(definition);
        this.nodeToReview = nodeToReview;
        this.messages = messages;
    }

    /**
     * Resolves the selected node path, calls the review API, and displays the result
     * as an info notification in the Magnolia message bar.
     */
    @Override
    public void execute() throws ActionExecutionException {
        try {
            Node node = this.nodeToReview.getJcrItem();
            String path = node.getPath();
            String review = sendReviewRequest(path).review();
            messages.sendLocalMessage(
                    new Message(
                            MessageType.INFO,
                            String.format("Script Review for %s", path),
                            review));
        } catch (RuntimeException | RepositoryException | IOException | InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Sends a GET request to the review API for the given script path.
     *
     * @param path JCR path of the script node.
     * @return Parsed {@link ReviewResponse} from the API.
     */
    private ReviewResponse sendReviewRequest(String path) throws IOException, InterruptedException, RepositoryException {
        HttpRequest request = HttpRequest.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .uri(URI.create(getGroovyGeneratorUrl(REVIEW_PATH, path)))
                .header("Content-Type", "application/json")
                .header("X-API-Key", getKeystoreValue(API_KEY_PATH))
                .timeout(Duration.ofSeconds(REQUEST_TIMEOUT))
                .GET().build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new IOException("Unexpected response status: " + response.statusCode() + " — " + response.body());
        }

        return mapReviewResponse(response.body());
    }

    /**
     * Maps the raw JSON response body to a {@link ReviewResponse} record.
     *
     * @param response Raw JSON string from the review API.
     * @return Parsed {@link ReviewResponse}.
     */
    private static ReviewResponse mapReviewResponse(String response) throws JsonProcessingException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(response);

        return new ReviewResponse(
                root.path("success").asBoolean(),
                root.path("path").asText(),
                root.path("review").asText());
    }

    /** Response payload received from the review API. */
    private record ReviewResponse(boolean success, String path, String review) {}
}