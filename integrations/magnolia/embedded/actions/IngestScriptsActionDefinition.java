package com.sample.cms.embedded.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.contentapp.action.JcrCommandActionDefinition;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@ActionType("ingestScriptsAction")
public class IngestScriptsActionDefinition extends JcrCommandActionDefinition {
    public IngestScriptsActionDefinition() {
        this.setImplementationClass(IngestScriptsAction.class);
    }
}
