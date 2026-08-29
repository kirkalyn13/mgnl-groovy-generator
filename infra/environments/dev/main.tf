module "networking" {
  source                = "git::https://github.com/kirkalyn13/platform-infra.git//modules/networking"
  app_name              = var.app_name
  vpc_cidr              = var.vpc_cidr
  aws_region            = var.aws_region
  create_public_subnet  = var.create_public_subnet
  create_private_subnet = var.create_private_subnet
}

module "ec2" {
  source          = "git::https://github.com/kirkalyn13/platform-infra.git//modules/ec2"
  app_name        = var.app_name
  vpc_id          = module.networking.vpc_id
  subnet_id       = module.networking.public_subnet_id
  ami_id          = var.ami_id
  instance_type   = var.instance_type
  app_port        = var.app_port
  app_jar_path    = var.app_jar_path
  secret_arns     = module.secrets.secret_arns
  parameter_names = module.parameter_store.parameter_names
}

module "dns" {
  source      = "git::https://github.com/kirkalyn13/platform-infra.git//modules/dns"
  app_name    = var.app_name
  domain_name = var.domain_name
  instance_ip = module.ec2.instance_public_ip
}

module "secrets" {
  source   = "git::https://github.com/kirkalyn13/platform-infra.git//modules/secrets"
  app_name = var.app_name
  secrets = {
    api_key             = var.api_key
    qdrant_api_key      = var.qdrant_api_key
    magnolia_username   = var.magnolia_username
    magnolia_password   = var.magnolia_password
    langfuse_secret_key = var.langfuse_secret_key
    langfuse_public_key = var.langfuse_public_key
  }
}

module "parameter_store" {
  source   = "git::https://github.com/kirkalyn13/platform-infra.git//modules/parameter_store"
  app_name = var.app_name
  parameters = {
    qdrant_url                         = var.qdrant_url
    collection_name                    = var.collection_name
    llm_mode                           = var.llm_mode
    ollama_url                         = var.ollama_url
    ollama_embedding_model             = var.ollama_embedding_model
    ollama_llm                         = var.ollama_llm
    tool_call_llm                      = var.tool_call_llm
    magnolia_scripts_rest_delivery_url = var.magnolia_scripts_rest_delivery_url
    langfuse_base_url                  = var.langfuse_base_url
    redis_url                          = var.redis_url
    session_ttl_minutes                = var.session_ttl_minutes
    session_size                       = var.session_size
  }
}

module "cloudwatch" {
  source   = "git::https://github.com/kirkalyn13/platform-infra.git//modules/cloudwatch"
  app_name = var.app_name
  env      = var.env
}
