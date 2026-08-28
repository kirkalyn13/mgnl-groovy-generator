output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = module.ec2.instance_public_ip
}

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.dns.zone_id
}

output "app_url" {
  description = "App domain"
  value       = "http://${var.domain_name}:${var.app_port}"
}

output "secret_arns" {
  description = "ARN of the API key secret"
  value       = module.secrets.secret_arns
}

output "parameter_names" {
  description = "Parameter Store names"
  value       = module.parameter_store.parameter_names
}
