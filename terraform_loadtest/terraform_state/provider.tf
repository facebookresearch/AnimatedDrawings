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
  profile = "arn:aws:iam::790537050551:role/iam-role-dev-demo-sketch-out-animations-write"
  // access_key = var.AWS_ACCESS_KEY_ID
  // secret_key = var.AWS_SECRET_ACCESS_KEY
  #assume_role {
  #  role_arn     = "arn:aws:iam::790537050551:role/iam-role-dev-demo-sketch-out-animations-write"
  #}
}
