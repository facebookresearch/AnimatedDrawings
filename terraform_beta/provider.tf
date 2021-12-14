terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.67.0"
    }
  }
}

provider "aws" {
  region     = "us-east-2"
  profile = "arn:aws:iam::223420189915:role/ML_DEVOPS_INSTANCE_ROLE"
}


resource "aws_s3_bucket" "tf_remote_state" {
  bucket = "sketch-beta-terraform-s3-backend"
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


#locking part

resource "aws_dynamodb_table" "tf_remote_state_locking" {
  hash_key = "LockID"
  name = "sketch-beta-terraform-s3-backend-locking"
  attribute {
    name = "LockID"
    type = "S"
  }
  billing_mode = "PAY_PER_REQUEST"
}


data "aws_vpc" "default" {
  default = true
}
locals {
  vpc_id = "${data.aws_vpc.default.id}"
}