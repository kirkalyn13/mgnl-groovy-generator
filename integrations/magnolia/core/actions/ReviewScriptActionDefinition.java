package com.sample.cms.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.api.action.ConfiguredActionDefinition;

@ActionType("reviewScriptAction")
public class ReviewScriptActionDefinition extends ConfiguredActionDefinition {
    public ReviewScriptActionDefinition() {
        this.setImplementationClass(ReviewScriptAction.class);
    }
}
