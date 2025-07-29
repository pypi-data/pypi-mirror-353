terraform {
  required_version = "~> 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.93.0"
    }
  }

  backend "s3" {
    bucket         = "fluidattacks-terraform-states-prod"
    encrypt        = true
    key            = "labels.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform_state_lock"
  }
}

provider "aws" {
  region = "us-east-1"
}
