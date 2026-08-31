# Magnolia CMS Integration

This module integrates the Magnolia Groovy Generator API into Magnolia CMS as a custom action, allowing developers to generate and save Groovy scripts directly from the Magnolia admincentral without leaving the CMS.

![Magnolia Integration Demo](../../assets/mgnl-demo.gif)
[▶ Watch Demo](https://drive.google.com/file/d/12dixAMERaaCbuTUxM14ih4Z9g-1qXISh/view?usp=sharing)

## Dialog

The dialog (`generateScript.yaml`) exposes four fields:

| Field | Type | Description |
|---|---|---|
| `name` | Text area | Desired script name |
| `query` | Text area | Natural language prompt describing the desired script |
| `workspaces` | Multi-value | JCR workspace names to scope the script (e.g. `website`, `dam`) |
| `properties` | Multi-value | JCR property names the script should reference |


## Action

[`GenerateScriptAction.java`](./core/actions/GenerateScriptAction.java) extends Magnolia's `CommitAction` and:

- Reads field values from the dialog form
- Sends a `POST` request to the configured generator API
- Parses the JSON response
- Saves the script as a `mgnl:content` node in the `scripts` workspace
- Sends a Magnolia message bar notification on success


## Configuration

Add the groovy generator API URL and API Key to the Passwords app with the following paths, respectively:

- `/groovy-generator/url` = `http://localhost:8000`
- `/groovy-generator/api-key` = `<api-key-value>`

For a deployed environment, replace `localhost:8000` with the URL of your hosted FastAPI instance.


## Action Definition

The action is registered as an `openDialogAction` that opens the generate dialog.

```yaml
generateScript:
  label: Generate Script
  icon: icon-add-fav
  $type: openDialogAction
  dialogId: sample-lm:generateScript
  allowModifications: false
  availability:
    writePermissionRequired: true
    root: true
```

## Actionbar

The action is surfaced in the root section for this use case:

```yaml
sections:
  root:
    groups:
      edit:
        items:
          - generateScript
```

## Notes

- `allowModifications: false` is set on the action definition — the API will reject any query that attempts to modify, delete, or update content
- The generated script node name must be unique or not yet taken
- The action has a 120 second timeout to account for local LLM generation time

## Other Integrations

### Groovy Script Code Review API

[`ReviewScriptAction.java`](./core/actions/ReviewScriptAction.java) extends Magnolia's `AbstractAction` and:

- Sends a `GET` request to review the groovy script pulled from `/{script_path}`
- Sends a Magnolia message bar notification on success and review details

### Sample Response consumed from `GET /v1/scripts/review/{script_path}`:
```json
{
    "success": true,
    "path": "magnoliaModulesDependencies",
    "review": "Here's a code review for the provided Magnolia CMS Groovy script:\n\n1. **Naming Conventions**: Adhere to consistent naming conventions throughout the script..."
}
```

### Action Definition:
```yaml
reviewScript:
  label: Review Script
  icon: icon-instant_preview
  $type: reviewScriptAction
  availability:
    nodeTypes:
      - mgnl:content
```

### Groovy Script Describe Script API

[`DescribeScriptAction.java`](./core/actions/DescribeScriptAction.java) extends Magnolia's `AbstractAction` and:

- Sends a `GET` request to describe or explain the groovy script pulled from `/{script_path}`
- Sends a Magnolia message bar notification on success and review details

### Sample Response consumed from `GET /v1/scripts/describe/{script_path}`:
```json
{
    "success": true,
    "path": "magnoliaModulesDependencies",
    "description": "This Groovy script is a utility for inspecting Magnolia module dependencies and version information..."
}
```

### Action Definition:
```yaml
describeScript:
  label: Describe Script
  icon: icon-content-item
  $type: describeScriptAction
  availability:
    nodeTypes:
      - mgnl:content
```

> **Note:** Scripts should be exposed via REST Delivery (see [scripts REST Delivery config](./light-modules/sample-lm/restEndpoints/delivery/scripts_v1.yaml)) and the request URL is specified in the `.env` file