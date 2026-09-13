## Embedded (Magnolia-Native) Approach

This is a proof-of-concept exploring an alternative, Magnolia-native implementation of the Groovy Generator.

- **Primary approach:** calls an external FastAPI service over HTTP
- **This variant:** runs the full RAG pipeline directly inside Magnolia, eliminating the middleman service
  - Embedding
  - Vector search
  - Generation

**Trade-off:**
- Couples the module tightly to Magnolia's runtime and dependency footprint
- In exchange, removes the external service hop entirely

## Architecture

```mermaid
flowchart RL

    subgraph CLIENT["Client"]
        direction TB
        MAGNOLIA["📝 Magnolia CMS
        Custom Action"]
    end

    MAGNOLIA -->|"1. Embed query"| EMBED["🧠 Embedding Service
    LLM e.g. Gemini"]
    EMBED -->|"2. Query vector"| VSTORE["🗄️ Vector Store
    e.g. Qdrant"]
    VSTORE -->|"3. Retrieved context"| MAGNOLIA
    MAGNOLIA -->|"4. Prompt + context"| GENERATE["⚡ Generation Service
    LLM e.g. Gemini"]
    GENERATE -->|"5. Generated script"| MAGNOLIA
    MAGNOLIA -->|"6. Save script node"| JCR["💾 JCR
    scripts workspace"]

    style MAGNOLIA fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#000000
    style CLIENT fill:#ffffff,stroke:#16a34a,stroke-width:1px,stroke-dasharray:5,color:#000000
    style EMBED fill:#fefce8,stroke:#ca8a04,stroke-width:2px,color:#000000
    style GENERATE fill:#fefce8,stroke:#ca8a04,stroke-width:2px,color:#000000
    style VSTORE fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#000000
    style JCR fill:#fdf4ff,stroke:#a855f7,stroke-width:2px,color:#000000
```

Unlike the loosely-coupled approach, there's no standalone REST API or FastAPI server — Magnolia calls the LLM and vector store directly, in-process. Embedding, retrieval, and generation all happen synchronously within the dialog action's execution, and the round-trip to build context and generate the script occurs entirely inside a single Magnolia request thread.

See the [`architecture discussion`](../../../README.md#architecture) for the full reasoning behind keeping the FastAPI approach as the primary implementation, with this serving as a secondary, scoped demo.

### Configuration

Before use, configure the following values via the Magnolia **Passwords app** at their respective paths:

| Path | Description |
|---|---|
| `/groovy-generator/embedded/llm/embed-endpoint` | Embedding endpoint URL for the LLM (e.g. Gemini) |
| `/groovy-generator/embedded/llm/generate-endpoint` | Generation endpoint URL for the LLM (e.g. Gemini) |
| `/groovy-generator/embedded/llm/model` | Model identifier to use for generation |
| `/groovy-generator/embedded/llm/api-key` | API key for the LLM provider |
| `/groovy-generator/embedded/vector-store/url` | Base URL for the vector store (e.g. Qdrant) |
| `/groovy-generator/embedded/vector-store/api-key` | API key for the vector store, if authentication is enabled |
| `/groovy-generator/embedded/vector-store/collection-name` | Name of the collection to search for retrieval context |

### Action Usage

Set the dialog's commit action `$type` to select which implementation runs:

```yaml
$type: generateScriptAction  # generateScriptAction (FastAPI) or generateScriptEmbeddedAction (Magnolia-native)
```