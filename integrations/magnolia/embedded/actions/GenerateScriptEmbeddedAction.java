package com.sample.cms.embedded.actions;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vaadin.ui.UI;
import info.magnolia.context.MgnlContext;
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
import org.apache.commons.lang.StringUtils;
import com.sample.cms.embedded.service.EmbeddingService;
import com.sample.cms.embedded.dto.ScoredPoint;
import com.sample.cms.embedded.service.VectorStoreService;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.RepositoryException;
import javax.jcr.Session;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

import static com.sample.cms.util.GroovyGeneratorConstants.*;
import static com.sample.cms.embedded.util.EmbeddedGroovyGeneratorConstants.TOP_K;

/**
 * Dialog commit action that runs the full RAG pipeline in-process — embedding the user's query,
 * retrieving similar context from vector store, generating a Groovy script via LLM, and saving the
 * result to the scripts workspace — without relying on the external FastAPI generator service.
 */
public class GenerateScriptEmbeddedAction extends CommitAction<GenerateScriptEmbeddedActionDefinition> {

    private final FormView<GenerateScriptEmbeddedActionDefinition> form;
    private final MessagesManager messages;
    private final EmbeddingService embeddingService;
    private final VectorStoreService vectorStoreService;
    private final ObjectMapper objectMapper;

    /**
     * @param definition            Action definition containing configuration.
     * @param closeHandler          Handles closing the dialog after execution.
     * @param valueContext          Provides the current JCR node context.
     * @param form                  The dialog form view to read field values from.
     * @param datasource            Datasource bound to the content app.
     * @param datasourceObservation Triggers UI refresh after datasource changes.
     * @param messages              Sends notifications to the Magnolia message bar.
     * @param embeddingService      Generates query embeddings and calls the LLM for script generation.
     * @param vectorStoreService    Performs similarity search against the vector store for retrieval context.
     * @param objectMapper          Parses the JSON-wrapped script payload returned by the LLM.
     */
    @Inject
    public GenerateScriptEmbeddedAction(
            GenerateScriptEmbeddedActionDefinition definition,
            CloseHandler closeHandler,
            ValueContext<GenerateScriptEmbeddedActionDefinition> valueContext,
            FormView<GenerateScriptEmbeddedActionDefinition> form,
            Datasource<GenerateScriptEmbeddedActionDefinition> datasource,
            DatasourceObservation.Manual datasourceObservation,
            MessagesManager messages,
            EmbeddingService embeddingService,
            VectorStoreService vectorStoreService,
            ObjectMapper objectMapper) {
        super(definition, closeHandler, valueContext, form, datasource, datasourceObservation);
        this.form = form;
        this.messages = messages;
        this.embeddingService = embeddingService;
        this.vectorStoreService = vectorStoreService;
        this.objectMapper = objectMapper;
    }

    /**
     * Validates the form, reads the query and dialog fields, embeds the query, retrieves similar
     * context from the vector store, generates a Groovy script via the LLM, saves it to the
     * scripts workspace, and notifies the user on success.
     */
    @Override
    public void execute() throws ActionExecutionException {
        if (!super.validateForm()) return;
        super.execute();

        try {
            String scriptName = form.getPropertyValue(SCRIPT_NAME_PROPERTY).orElseThrow().toString();
            String query = String.format("%s: %s", QUERY_PREFIX, form.getPropertyValue(QUERY_PROPERTY).orElseThrow());
            List<String> workspaces = form.getPropertyValue(WORKSPACES_PROPERTY).stream().map(Object::toString).toList();
            List<String> properties = form.getPropertyValue(PROPERTIES_PROPERTY).stream().map(Object::toString).toList();
            Boolean allowModifications = ((GenerateScriptEmbeddedActionDefinition) this.getDefinition()).getAllowModifications();

            float[] queryVector = embeddingService.embed(query);
            List<ScoredPoint> matches = vectorStoreService.search(queryVector, TOP_K);

            String script = generateScript(query, matches, workspaces, properties, allowModifications);

            saveGeneratedScript(scriptName, script);
            messages.sendLocalMessage(new Message(MessageType.INFO, "Script Generated",
                    String.format("Successfully Generated Script: \n %s", script)));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Builds the retrieval-augmented prompt from the query and matched context, sends it to the
     * LLM, and unwraps the resulting JSON payload to extract the generated script.
     *
     * @param query              Natural language query describing the desired script.
     * @param matches            Retrieved vector store matches used as grounding context.
     * @param workspaces         List of JCR workspace names to scope the script to.
     * @param properties         List of JCR property names relevant to the query.
     * @param allowModifications Boolean to specify if modification script requests are allowed.
     * @return The raw Groovy script text extracted from the LLM's JSON response.
     * @throws IOException If the LLM flags the generated script as unsafe.
     */
    private String generateScript(String query, List<ScoredPoint> matches, List<String> workspaces, List<String> properties, Boolean allowModifications) throws Exception {
        String context = matches.stream()
                .map(m -> String.valueOf(m.payload().get("text")))
                .collect(Collectors.joining("\n---\n"));
        String prompt = buildPrompt(query, context, workspaces, properties, allowModifications);
        String rawResponse = embeddingService.generate(prompt);

        JsonNode parsed = objectMapper.readTree(rawResponse);
        if (!parsed.path("is_safe").asBoolean(true)) {
            throw new IOException("Generated script flagged as unsafe, refusing to save.");
        }
        return parsed.path("script").asText();
    }

    /**
     * Saves the generated script as a {@code mgnl:content} node in the scripts workspace with the
     * given script name, then reloads AdminCentral so the new node is reflected in the browser.
     *
     * @param scriptName Preferred groovy script name.
     * @param code       The generated Groovy script content.
     */
    private void saveGeneratedScript(String scriptName, String code) throws RepositoryException {
        Session session = MgnlContext.getJCRSession(GROOVY_WORKSPACE);

        Node rootNode = session.getRootNode();
        Node scriptNode = rootNode.addNode(scriptName.trim().replace(" ", "-"), SCRIPT_NODE_TYPE);
        scriptNode.setProperty("script", true);
        scriptNode.setProperty("text", code);

        session.save();
        UI.getCurrent().getPage().reload();
    }

    /**
     * Assembles the retrieval-augmented generation prompt, instructing the LLM to respond with a
     * strict JSON structure containing the script and its validity/safety self-assessment.
     *
     * @param query              Natural language query describing the desired script.
     * @param context            Concatenated text of the retrieved vector store matches.
     * @param workspaces         List of JCR workspace names to scope the script to.
     * @param properties         List of JCR property names relevant to the query.
     * @param allowModifications Boolean to specify if modification script requests are allowed.
     * @return The fully assembled prompt string to send to the LLM.
     */
    private static String buildPrompt(String query, String context, List<String> workspaces, List<String> properties, Boolean allowModifications) {
        String workspacesClause = !workspaces.isEmpty()
                ? String.format("Target Magnolia workspaces: %s", workspaces)
                : StringUtils.EMPTY;
        String propertiesClause = !properties.isEmpty()
                ? String.format("The script must include the following properties: %s.", properties)
                : StringUtils.EMPTY;
        String modificationsClause = Boolean.TRUE.equals(allowModifications)
                ? "Modification scripts (create, update, delete) are allowed."
                : "Only read-only scripts are allowed — do not create, update, or delete content.";

        return String.format("""
            You are a Magnolia CMS Groovy script generator.
            Respond ONLY with a JSON object, no explanation, no markdown.
        
            Generate a Groovy script and return this exact structure:
            {
                "script": "the raw Groovy script here",
                "is_valid_groovy": true or false,
                "is_safe": true or false
            }
        
            Rules:
            - script must be raw Groovy only, no markdown, no code blocks
            - is_valid_groovy must be true if the script is valid Groovy
            - is_safe must be false if the script contains Runtime.exec, System.exit, File.delete, or shell commands
            %s
            %s
            %s
        
            Request: %s
            Context from examples: %s
            """, workspacesClause, propertiesClause, modificationsClause, query, context);
    }
}