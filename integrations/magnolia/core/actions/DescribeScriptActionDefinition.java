package com.sample.cms.actions;

import info.magnolia.ui.api.action.ActionType;
import info.magnolia.ui.api.action.ConfiguredActionDefinition;

@ActionType("describeScriptAction")
public class DescribeScriptActionDefinition extends ConfiguredActionDefinition {
    public DescribeScriptActionDefinition() {
        this.setImplementationClass(DescribeScriptAction.class);
    }
}
