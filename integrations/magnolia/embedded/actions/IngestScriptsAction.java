package com.sample.cms.embedded.actions;

import info.magnolia.commands.CommandsManager;
import info.magnolia.context.Context;
import info.magnolia.ui.ValueContext;
import info.magnolia.ui.api.message.Message;
import info.magnolia.ui.api.message.MessageType;
import info.magnolia.ui.contentapp.action.JcrCommandAction;
import info.magnolia.ui.contentapp.async.AsyncActionExecutor;
import info.magnolia.ui.datasource.jcr.JcrDatasource;
import info.magnolia.ui.framework.message.MessagesManager;
import info.magnolia.ui.observation.DatasourceObservation;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.RepositoryException;
import java.util.HashMap;
import java.util.Map;

/**
 * Content app action that triggers the {@code ingestScripts} command, scoped to the currently
 * selected folder (or the workspace root if nothing is selected).
 */
public class IngestScriptsAction extends JcrCommandAction<Node, IngestScriptsActionDefinition> {
    private final ValueContext<Node> valueContext;
    private final CommandsManager commandsManager;
    private final MessagesManager messages;

    /**
     * @param definition            Action definition containing configuration.
     * @param commandsManager       Resolves and executes the registered ingest command.
     * @param valueContext          Provides the currently selected JCR node, if any.
     * @param context               Execution context passed to the base action.
     * @param asyncActionExecutor   Executes the action asynchronously, per the base class.
     * @param jcrDatasource         Datasource backing the base class's item resolution.
     * @param datasourceObservation Triggers UI refresh after datasource changes.
     * @param messages              Sends notifications to the Magnolia message bar.
     */
    @Inject
    public IngestScriptsAction(
            IngestScriptsActionDefinition definition,
            CommandsManager commandsManager,
            ValueContext<Node> valueContext,
            Context context,
            AsyncActionExecutor asyncActionExecutor,
            JcrDatasource jcrDatasource,
            DatasourceObservation.Manual datasourceObservation,
            MessagesManager messages) {
        super(definition, commandsManager, valueContext, context, asyncActionExecutor, jcrDatasource, datasourceObservation);
        this.valueContext = valueContext;
        this.commandsManager = commandsManager;
        this.messages = messages;
    }

    /**
     * Resolves the selected folder's path (defaulting to the workspace root), runs the ingest
     * command against it, and notifies the user on success.
     */
    @Override
    public void execute() {
        try {
            String folderPath = valueContext.getSingle()
                    .map(node -> {
                        try {
                            return node.getPath();
                        } catch (RepositoryException e) {
                            throw new RuntimeException(e);
                        }
                    })
                    .orElse("/");

            Map<String, Object> params = new HashMap<>();
            params.put("path", folderPath);

            commandsManager.executeCommand("sample-module", "ingestScripts", params);

            Message message = new Message(MessageType.INFO, "Scripts Ingested", "Successfully Ingested Scripts");
            messages.sendLocalMessage(message);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}