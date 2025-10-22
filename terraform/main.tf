terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "CropRecommendation"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# ========== ADD EC2 CONFIGURATION HERE ==========

# Security Group for EC2
resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "Security group for crop recommendation app"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-app-sg"
  }
}

# EC2 Instance
resource "aws_instance" "crop_app" {
  ami           = "ami-0f5ee92e2d63afc18"  # Amazon Linux 2 in ap-south-1
  instance_type = "t3.micro"  # ← Free Tier eligible and better performance
  key_name      = aws_key_pair.crop_app.key_name  # Add this line
  
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = module.vpc.public_subnets[0]
  associate_public_ip_address = true
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              service docker start
              usermod -a -G docker ec2-user
              
              # Install Docker Compose
              curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              echo "EC2 instance ready for Docker deployment!"
              EOF

  tags = {
    Name = "${var.project_name}-app-server"
  }
}

# Elastic IP (optional but recommended)
resource "aws_eip" "app" {
  instance = aws_instance.crop_app.id
  vpc      = true
  
  tags = {
    Name = "${var.project_name}-app-ip"
  }
}