variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1" 
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "crop-reco"  # Changed from "crop-recommendation"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}
