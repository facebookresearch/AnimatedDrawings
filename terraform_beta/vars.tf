variable "region" {
  type    = string
  default = "us-east-2"
}

variable "environment" {
  type    = string
  default = "beta"
}

variable "instance_iam_role" {
  type    = string
}

variable "subnets" {
  type = list
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
  default = 5
}


variable "autoscale_max_capacity" {
  default = 10
}


variable "alphapose_service_name" {
  default = "alphapose_service"
}

variable "animation_service_name" {
  default = "animation_service"
}

variable "sketch_service_name" {
  default = "sketch_service"
}


variable "desired_count" {
  default = 2
}

variable "target_capacity" {
  default = "2"
}

variable "application_name" {
  default = "sketch-kids-animation"
}

variable "www_domain_name" {
  default = "beta-demo-sketch-www.com"
}

variable "model_store_bucket" {
  default = "beta-demo-sketch-in-model-store"
}

variable "interim_bucket" {
  default = "beta-demo-sketch-out-interim-files"
}

variable "consents_bucket" {
  default = "beta-demo-sketch-out-consents"
}

variable "video_bucket" {
  default = "beta-demo-sketch-out-animations"
}

variable "private_hosted_zone_id" {
  type = string
}


variable "primary_dns_name" {
  type = string
}

variable "animation_ami_id" {
  default = "ami-08e0b00e3616220d8"
}

variable "animation_instance_type" {
  default = "c5.4xlarge"

}

variable "animation_key_pair" {
  default = "animation-ecs-gpu"
}

variable "public_hosted_zone_id" {
  type = string
}

variable "sketch_api_cert_arn" {
  type = string
}

variable "detectron_ami_id" {
  default = "ami-0a39b734183d5c064"
}

variable "detectron_instance_type" {
  default = "g4dn.2xlarge"
}

variable "detectron_key_pair" {
  default = "detectron-ecs-gpu"
}

variable "PROFILE_ARN" {
  type = string
}

variable "cloudfront_cert_arn" {
  type = string
}