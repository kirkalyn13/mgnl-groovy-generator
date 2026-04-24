# Magnolia CMS Integration

This module integrates the Magnolia Groovy Generator API into Magnolia CMS as a custom action, allowing developers to generate and save Groovy scripts directly from the Magnolia admincentral without leaving the CMS.

![Magnolia Integration Demo](../../assets/mgnl-demo.gif)
[▶ Watch Demo](https://drive.google.com/file/d/12dixAMERaaCbuTUxM14ih4Z9g-1qXISh/view?usp=sharing)

## Dialog

The dialog (`generateScript.yaml`) exposes three fields:

| Field | Type | Description |
|---|---|---|
| `query` | Text area | Natural language prompt describing the desired script |
| `workspaces` | Multi-value | JCR workspace names to scope the script (e.g. `website`, `dam`) |
| `properties` | Multi-value | JCR property names the script should reference |


## Action

`GenerateScriptAction.java` extends Magnolia's `CommitAction` and:

- Reads field values from the dialog form
- Sends a `POST` request to the configured generator API
- Parses the JSON response
- Saves the script as a timestamped `mgnl:content` node in the `scripts` workspace
- Sends a Magnolia message bar notification on success


## Configuration

Add the generator API URL to your Magnolia configuration properties file:

```properties
magnolia.groovyGenerator.url=http://localhost:8000/v1/generate
```

For a deployed environment, replace `localhost:8000` with the URL of your hosted FastAPI instance.


## Action Definition

The action is registered as an `openDialogAction` that opens the generate dialog.

```yaml
generateScript:
  label: Generate Script
  icon: icon-add-fav
  $type: openDialogAction
  dialogId: sample-lm:generateScript
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
- The generated script node is named with a `generated-script-` prefix and a timestamp to ensure uniqueness
- The action has a 120 second timeout to account for local LLM generation time

## Other Integrations

### Groovy Script Code Review API: `GET /v1/review/{script_path}`

Reviews the groovy script pulled from `/{script_path}` from a Magnolia CMS instance, which could potentially be integrated to a custom action.

> Scripts should be exposed via REST Delivery and the request URL is specified in the `.env` file

```json
{
    "success": true,
    "path": "magnoliaModulesDependencies",
    "description": "Here's a code review for the provided Magnolia CMS Groovy script:\n\n1. **Naming Conventions**: Adhere to consistent naming conventions throughout the script..."
}
```
