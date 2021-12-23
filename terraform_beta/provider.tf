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


# Backend Resources
resource "aws_s3_bucket" "tf_remote_state" {
  bucket = "terraform-state-sketch-animation-${var.environment}"
  lifecycle {
    prevent_destroy = true
  }
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "tf_remote_state_locking" {
  hash_key = "LockID"
  name = "terraform-lock-sketch-animation-${var.environment}"
  attribute {
    name = "LockID"
    type = "S"
  }
  billing_mode = "PAY_PER_REQUEST"
}

# Backend Configuration
terraform {
  backend "s3" {
    bucket         = "terraform-state-sketch-animation-beta"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "terraform-lock-sketch-animation-beta"
    encrypt        = true
  }
}