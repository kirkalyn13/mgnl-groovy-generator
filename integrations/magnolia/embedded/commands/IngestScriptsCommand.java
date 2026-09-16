package com.sample.cms.embedded.commands;

import info.magnolia.cms.util.QueryUtil;
import info.magnolia.commands.MgnlCommand;
import info.magnolia.context.Context;
import com.sample.cms.embedded.dto.IngestPoint;
import com.sample.cms.embedded.service.EmbeddingService;
import com.sample.cms.embedded.service.VectorStoreService;
import com.sample.cms.util.GroovyGeneratorConstants;

import javax.inject.Inject;
import javax.jcr.Node;
import javax.jcr.NodeIterator;
import javax.jcr.RepositoryException;
import javax.jcr.query.Query;
import java.util.ArrayList;
import java.util.List;

/**
 * Command that walks the scripts workspace under a given path, embeds each script, and upserts
 * the results into the vector store for retrieval-augmented generation. Runnable from the UI or
 * a scheduler.
 */
public class IngestScriptsCommand extends MgnlCommand {
    private final VectorStoreService vectorStoreService;
    private final EmbeddingService embeddingService;

    /**
     * @param vectorStoreService Performs the embedding upsert against the vector store.
     * @param embeddingService   Generates embeddings for each script during ingestion.
     */
    @Inject
    public IngestScriptsCommand(VectorStoreService vectorStoreService, EmbeddingService embeddingService) {
        this.vectorStoreService = vectorStoreService;
        this.embeddingService = embeddingService;
    }

    /**
     * Queries all script nodes under the given path (or the workspace root if none is provided),
     * builds an {@link IngestPoint} per script, and upserts them into the vector store.
     *
     * @param context Execution context, optionally holding a {@code path} param to scope the query.
     * @return {@code true} on successful ingestion.
     */
    @Override
    public boolean execute(Context context) throws Exception {
        try {
            List<IngestPoint> ingestData = new ArrayList<>();
            String path = context.get("path") != null ? context.get("path").toString() : "/";
            String query = String.format("SELECT * FROM [mgnl:content] WHERE ISDESCENDANTNODE('%s')", path);
            NodeIterator nodes = QueryUtil.search(
                    GroovyGeneratorConstants.GROOVY_WORKSPACE,
                    query,
                    Query.JCR_SQL2,
                    "mgnl:content");

            while (nodes.hasNext()) {
                Node node = nodes.nextNode();
                String scriptID = node.getIdentifier();
                String scriptText = node.getProperty("text").getString();

                IngestPoint ingestPoint = new IngestPoint(scriptID, scriptText);
                ingestData.add(ingestPoint);
            }

            vectorStoreService.upsert(ingestData, embeddingService);

            return true;
        } catch (RepositoryException e) {
            throw new IllegalStateException("Repository exception occurred: ", e);
        }
    }
}
