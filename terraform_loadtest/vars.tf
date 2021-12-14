variable "region" {
    type        = string
    default = "us-east-2"
}

variable "environment" {
    type        = string
    default = "loadtest"
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

variable "detectron_gpu_container_name" {
    default = "detectron_gpu_api_container"
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
  default     = "detectron_service_Deploy"
}

variable "alphapose_service_name" {
  default     = "alphapose_service"
}

variable "animation_service_name" {
  default     = "animation_update_deploy"
}

variable "sketch_service_name" {
  default     = "sketch_update_image"
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

variable "desired_count" {
  default = 2
}

variable "target_capacity" {
  default = "2"
}

variable "application_name" {
  default = "detectron"
}

variable "www_domain_name" {
  default = "loadtest-demo-sketch-www.com"
}

variable "model_store_bucket" {
  default = "loadtest-demo-sketch-in-model-store"
}

variable "interim_bucket" {
  default = "loadtest-demo-sketch-out-interim-files"
}

variable "consents_bucket" {
  default = "loadtest-demo-sketch-out-consents"
}

variable "video_bucket" {
  default = "loadtest-demo-sketch-out-animations"
}

variable "private_hosted_zone_id" {
  type = string
}


variable "primary_dns_name" {
  default = ".dev.metademolab.com"
}

variable "ami_id" {
  default = "ami-08e0b00e3616220d8"
}

variable "instance_type" {
  default = "c5.4xlarge"
  
}

variable "key_pair" {
  default = "detectron-ecs-gpu"
}

variable "public_hosted_zone_id" {
  type = string
}

variable "sketch_api_cert_arn" {
  type = string
}