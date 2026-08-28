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
  description = "API key for the Spring Boot app — set via TF_VAR_api_key"
  type        = string
  sensitive   = true
}
