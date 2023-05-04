terraform {
  required_version = ">=1.4.6"
}

provider "aws" {
  region = "ap-northeast-1"
}

module "initializer" {
  source = "../../../modules/initializer"
  env = "dev"
}

