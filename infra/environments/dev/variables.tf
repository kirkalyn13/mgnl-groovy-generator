variable "app_name" {
  type    = string
  default = "mgnl-groovy-generator"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "create_public_subnet" {
  type    = bool
  default = false
}

variable "create_private_subnet" {
  type    = bool
  default = true
}

variable "ami_id" {
  description = "AMI ID — dummy value is fine for LocalStack"
  type        = string
  default     = "ami-00000000"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "app_port" {
  type    = number
  default = 8080
}

variable "app_jar_path" {
  type    = string
  default = "/opt/app/mgnl-groovy-generator.jar"
}

variable "domain_name" {
  type    = string
  default = "mgnl-groovy-generator.dev"
}

variable "api_key" {
  description = "API key for the application — set via TF_VAR_api_key"
  type        = string
  sensitive   = true
}
variable "qdrant_url" {
  description = "Qdrant URL"
  type        = string
  sensitive   = true
}

variable "qdrant_api_key" {
  description = "Qdrant API Key"
  type        = string
  sensitive   = true
}

variable "magnolia_username" {
  description = "Magnolia CMS instance username"
  type        = string
  sensitive   = true
}

variable "magnolia_password" {
  description = "Magnolia CMS instance password"
  type        = string
  sensitive   = true
}

variable "langfuse_secret_key" {
  description = "Langfuse Secret Key"
  type        = string
  sensitive   = true
}

variable "langfuse_public_key" {
  description = "Langfuse Public Key"
  type        = string
  sensitive   = true
}

variable "collection_name" {
  description = "Qdrant target collection name"
  type        = string
  default     = "magnolia_groovies"
}

variable "llm_mode" {
  description = "Preferred LLM source e.g. Ollama, OpenAI, etc."
  type        = string
  default     = "ollama"
}

variable "ollama_url" {
  description = "Ollama URL"
  type        = string
  default     = "http://localhost:11434"
}

variable "ollama_embedding_model" {
  description = "Embedding model name"
  type        = string
  default     = "nomic-embed-text"
}

variable "ollama_llm" {
  description = "Gen AI model name"
  type        = string
  default     = "mistral"
}

variable "tool_call_llm" {
  description = "Tool calling model name"
  type        = string
  default     = "qwen3.5"
}

variable "magnolia_scripts_rest_delivery_url" {
  description = "Magnolia CMS scripts REST Delivery endpoint base URL"
  type        = string
  default     = "http://127.0.0.1:8080/.rest/delivery/scripts/v1"
}

variable "langfuse_base_url" {
  description = "Langfuse base URL"
  type        = string
  default     = "https://us.cloud.langfuse.com"
}

variable "redis_url" {
  description = "Redis URL"
  type        = string
  default     = "redis://localhost:6379"
}

variable "session_ttl_minutes" {
  description = "Session TTL in minutes"
  type        = number
  default     = 30
}

variable "session_size" {
  description = "Session size"
  type        = number
  default     = 10
}