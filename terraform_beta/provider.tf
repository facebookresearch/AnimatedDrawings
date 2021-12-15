terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.67.0"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.PROFILE_ARN
}


terraform {
  backend "s3" {
    bucket         = "sketch-animation-terraform-s3-backend"
    key            = "terraform/backend/terraform_aws.tfstate"
    region         = "us-east-2"
    dynamodb_table = "sketch-animation-terraform-s3-backend-locking"
    encrypt        = true
  }
}

data "aws_vpc" "default" {
  default = true
}
locals {
  vpc_id = data.aws_vpc.default.id
}

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}
