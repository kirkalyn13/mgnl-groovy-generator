# Magnolia Groovy Generator

A RAG-powered web app for generating Magnolia CMS Groovy scripts using natural language prompts.

Live Site: [mgnl-groovy-generator-app](https://mgnl-groovy-generator-app.vercel.app/)

![Demo](./assets/app-demo.gif)



## Overview

Magnolia Groovy Generator is a full-stack portfolio project that combines a FastAPI backend with a React + Vite frontend to generate context-aware Groovy scripts for Magnolia CMS. It uses Retrieval-Augmented Generation (RAG) to ground script generation on a curated set of example scripts, ensuring outputs are accurate and idiomatic.



## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Python |
| LLM & Embeddings | Ollama (`mistral`, `nomic-embed-text`) |
| Vector Store | Qdrant |
| RAG Framework | LlamaIndex |

---

## Features

- Natural language to Groovy script generation
- RAG pipeline grounded on example Magnolia CMS scripts
- Expected properties input — tag-based field to guide script output
- Input guard rails — blocks non-Groovy and modification requests
- Output guard rails — validates and sanitizes generated scripts
- Retry logic — automatically retries if output contains unwanted content
- Rate limiting — 1 request per second per client
- Fully local — runs entirely on your machine with no cloud API required

---


## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running

---

## Getting Started
 
### 1. Clone the repository
 
```bash
git clone https://github.com/kirkalyn13/mgnl-groovy-generator
cd mgnl-groovy-generator
```
 
### 2. Set up environment variables
 
```bash
cp .env.example .env
```
 
Edit `.env`:
 
```env
QDRANT_URL=https://your-cluster-url
QDRANT_API_KEY=your_qdrant_key
COLLECTION_NAME=docs_collection_name
LLM_MODE=preferred_llm_mode_like_ollama
OLLAMA_URL=https://your-ollama-url
OLLAMA_EMBEDDING_MODEL=your_embedding_model
OLLAMA_LLM=your_ollama_llm
```
 
### 3. Install Python dependencies
 
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 
### 4. Pull Ollama models
 
```bash
ollama pull nomic-embed-text
ollama pull mistral
```
 
### 5. Ingest your Groovy scripts
 
Add your `.groovy` example files to the `data/` folder, then run:
 
```bash
python ingest.py
```
 
### 6. Start the API
 
```bash
uvicorn app:app --reload --port 8000
```
 
 
---
 
## API Reference
 
Interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs) once the server is running.
 
### `POST /generate`
 
Generate a Magnolia CMS Groovy script from a natural language query.
 
**Request**
```json
{
  "query": "Generate a Groovy script to retrieve all published pages",
  "properties": ["pageTitle", "activationStatus", "path"]
}
```
 
**Response**
```json
{
  "success": true,
  "query": "Generate a Groovy script to retrieve all published pages",
  "response": "def hm = MgnlContext.getHierarchyManager...",
  "retries": 0,
  "message": null
}
```
 
### `POST /ingest`
 
Ingest `.groovy` files from the data folder into Qdrant.
 
**Request**
```json
{
  "path": "./data"
}
```
 
**Response**
```json
{
  "success": true,
  "message": "Successfully ingested 12 documents."
}
```

## Improvements

- Ingest more well-documented and labeled Groovy scripts.


## Authors

- [Engr. Kirk Alyn Santos](https://github.com/kirkalyn13)

## License

MIT