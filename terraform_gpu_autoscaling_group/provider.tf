terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.67.0"
    }
  }
}

provider "aws" {
  region     = var.region
  profile = "arn:aws:iam::790537050551:role/iam-role-dev-demo-sketch-out-animations-write"
  //profile = var.PROFILE_ARN
}

data "aws_vpc" "default" {
  default = true
} 
locals {
  vpc_id = "${data.aws_vpc.default.id}"
} 

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}