terraform {
  backend "s3" {
    bucket = "fcx-terraform-backend-states"
    key    = "terraform/states/histogram"
    region = "us-west-2"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67.0"
    }
  }

  required_version = "~> 1.2"
}