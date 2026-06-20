module "networking" {
  source     = "git::https://github.com/kirkalyn13/platform-infra.git//modules/networking"
  app_name   = var.app_name
  vpc_cidr   = var.vpc_cidr
  aws_region = var.aws_region
}

module "secrets" {
  source      = "git::https://github.com/kirkalyn13/platform-infra.git//modules/secrets"
  app_name    = var.app_name
  api_key     = var.api_key
}

module "ec2" {
  source            = "git::https://github.com/kirkalyn13/platform-infra.git//modules/ec2"
  app_name          = var.app_name
  vpc_id            = module.networking.vpc_id
  subnet_id         = module.networking.public_subnet_id
  ami_id            = var.ami_id
  instance_type     = var.instance_type
  app_port          = var.app_port
  app_jar_path      = var.app_jar_path
  api_secret_arn    = module.secrets.secret_arn
}

module "dns" {
  source      = "git::https://github.com/kirkalyn13/platform-infra.git//modules/dns"
  app_name    = var.app_name
  domain_name = var.domain_name
  instance_ip = module.ec2.instance_public_ip
}
