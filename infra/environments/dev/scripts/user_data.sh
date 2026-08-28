#!/bin/bash
set -e

# Update and install dependencies
yum update -y
yum install -y gcc gcc-c++ make git awscli

# Install Python 3.11
yum install -y python3.11 python3.11-pip
alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
systemctl enable ollama
systemctl start ollama
ollama pull mistral
ollama pull nomic-embed-text

# Install app dependencies
pip3 install --upgrade pip
pip3 install \
  "llama-index>=0.14.0" \
  "llama-index-vector-stores-qdrant>=0.9.0" \
  "llama-index-embeddings-ollama>=0.5.0" \
  "llama-index-llms-ollama>=0.5.0" \
  "llama-index-postprocessor-colbert-rerank>=0.3.0" \
  "qdrant-client>=1.17.0" \
  "fastapi>=0.135.3" \
  "uvicorn>=0.43.0" \
  "slowapi>=0.1.9" \
  "langchain>=1.2.15" \
  "langchain-ollama>=1.1.0" \
  "langchain-qdrant>=1.1.0" \
  "langchain-core>=1.3.0" \
  "langchain-community>=0.3.0" \
  "langgraph>=0.3.0" \
  "langfuse>=4.5.1" \
  "openinference-instrumentation-llama-index>=3.0.0" \
  "httpx>=0.27.0" \
  "python-dotenv>=1.0.0" \
  "pydantic-settings>=2.0.0" \
  "redis>=5.0.0" \
  "duckduckgo-search>=6.0.0" \
  "ollama>=0.3.1" \
  "nest-asyncio>=1.6.0"

# Build .env from Secrets Manager (by ARN) + Parameter Store (by name)
ENV_FILE="${app_jar_path}/.env"
mkdir -p "${app_jar_path}"
> "$ENV_FILE"

%{ for key, arn in secret_arns ~}
value=$(aws secretsmanager get-secret-value \
  --secret-id "${arn}" \
  --query SecretString --output text \
  --region "${aws_region}")
echo "$(echo ${key} | tr a-z A-Z)=$value" >> "$ENV_FILE"
%{ endfor ~}

%{ for key, name in parameter_names ~}
value=$(aws ssm get-parameter \
  --name "${name}" \
  --query Parameter.Value --output text \
  --region "${aws_region}")
echo "$(echo ${key} | tr a-z A-Z)=$value" >> "$ENV_FILE"
%{ endfor ~}

# Run FastAPI app
cd "${app_jar_path}"
nohup uvicorn main:app \
  --host 0.0.0.0 \
  --port ${app_port} \
  > /var/log/app.log 2>&1 &