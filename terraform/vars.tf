#variable "AWS_ACCESS_KEY_ID" {
#    type        = string
#}
#variable "AWS_SECRET_ACCESS_KEY" {
#    type        = string
#}

variable "region" {
    type        = string
    default = "us-east-2"
}

variable "TEAMNAME" {
    type        = string
    default = "ML_DEVOPS"
}

variable "environment" {
    type        = string
    default = "QA"
}


variable "qaenvironment" {
    type        = string
    default = "qa"
}

variable "vpc_id" {
    type        = string
    default = "vpc-0bdbb960"
}

variable "sketch_instance_arn" {
    type        = string
    default = "arn:aws:iam::790537050551:role/iam-role-dev-demo-sketch-out-animations-write"
}


variable "security_groups" {
    default = ["sg-0c9000062b58977f0", "sg-0e15f3169ff2af367"]
}

variable "subnets" {
    default = ["subnet-97fcd7db", "subnet-9daf6ce0", "subnet-d039b3bb"]
}

variable "detectron_container_name" {
    default = "detectron_container"
}

variable "alphapose_container_name" {
    default = "alphapose_container"
}

variable "animation_container_name" {
    default = "animation_container"
}

variable "sketch_container_name" {
    default = "sketch_api_container"
}

variable "account_id" {
    default = "790537050551"
}

variable "autoscale_enabled" {
  description = "Setup autoscale."
  default     = "true"
}

variable "autoscale_rpm_enabled" {
  description = "Setup autoscale for RPM."
  default     = "true"
}


variable "service_desired_count" {
  default     = 5
}


variable "autoscale_max_capacity" {
  default     = 10
}


variable "detectron_service_name" {
  default     = "Detectron_Service_Deploy"
}

variable "alphapose_service_name" {
  default     = "Alphapose_Service_Deploy"
}

variable "animation_service_name" {
  default     = "Animation_Service_Deploy"
}

variable "sketch_service_name" {
  default     = "Sketch_Service_New_Deploy"
}




variable "detectron_image" {
  default = "790537050551.dkr.ecr.us-east-2.amazonaws.com/ml_devops_modelzoo_repo:latest"
}

variable "alphapose_image" {
  default = "790537050551.dkr.ecr.us-east-2.amazonaws.com/alphapose_runtime:latest"
}

variable "animation_image" {
  default = "790537050551.dkr.ecr.us-east-2.amazonaws.com/animation_model:latest"
}

variable "sketch_image" {
  default = "790537050551.dkr.ecr.us-east-2.amazonaws.com/sketch_api:latest"
}


variable "ami_id" {
  default = "ami-0ad5ad4fc21853cae"
}




variable "target_capacity" {
  default = "2"
}

variable "application_name" {
  default = "detectron"
}

variable "detect_ec2_service_name" {
  default = "DETECT_LOADTEST_SERVICE_DEPLOY_UPDATE"
}

variable "detect_ec2_te_name" {
  default = "D_TE_TEST2"
}

variable "instance_type" {
  default = "p2.xlarge"
}


variable "alpha_ec2_service_name" {
  default = "ALPHA_EC2_QA"
}



variable "model_domain_name" {
  default = "www.my-model.com"
}

variable "www_domain_name" {
  default = "qa-demo-sketch-www.com"
}

variable "detecron_repo_name" {
  default = "qa-demo-sketch-www.com"
}
