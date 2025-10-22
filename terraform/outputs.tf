output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "app_public_ip" {
  description = "Public IP of the application server"
  value       = aws_eip.app.public_ip
}

output "ssh_connection" {
  description = "SSH connection command"
  value       = "ssh ec2-user@${aws_eip.app.public_ip}"
}

