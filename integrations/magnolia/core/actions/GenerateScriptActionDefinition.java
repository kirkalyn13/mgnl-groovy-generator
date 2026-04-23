package com.sample.cms.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.contentapp.action.CommitActionDefinition;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@ActionType("generateScriptAction")
public class GenerateScriptActionDefinition extends CommitActionDefinition {
    private Boolean allowModifications = false;
    public GenerateScriptActionDefinition() {
        this.setImplementationClass(GenerateScriptAction.class);
    }
}

