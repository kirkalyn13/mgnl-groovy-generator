package com.sample.cms.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.contentapp.action.CommitActionDefinition;

@ActionType("generateScriptAction")
public class GenerateScriptActionDefinition extends CommitActionDefinition {
    public GenerateScriptActionDefinition() {
        this.setImplementationClass(GenerateScriptAction.class);
    }
}
