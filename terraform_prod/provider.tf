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
  //profile = var.PROFILE_ARN
}


terraform {
   backend "s3" {
     bucket = "sketch-animation-terraform-s3-backend"
     key = "terraform/backend/terraform_aws.tfstate"
     region = "us-east-2"
     dynamodb_table = "sketch-animation-terraform-s3-backend-locking"
     encrypt = true
   }
 }
