package com.sample.cms.embedded.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.contentapp.action.CommitActionDefinition;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@ActionType("generateScriptEmbeddedAction")
public class GenerateScriptEmbeddedActionDefinition extends CommitActionDefinition {
    private Boolean allowModifications = false;
    public GenerateScriptEmbeddedActionDefinition() {
        this.setImplementationClass(GenerateScriptEmbeddedAction.class);
    }
}
