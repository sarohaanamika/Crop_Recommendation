terraform {
  backend "s3" {
    bucket         = "crop-recommendation-terraform-state-mumbai-anamikasaroha"
    key            = "prod/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}