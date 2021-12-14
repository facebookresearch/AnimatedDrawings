variable "region" {
    type        = string
    default = "us-east-2"
}

variable "environment" {
    type        = string
    default = "beta"
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

variable "autoscale_enabled" {
  description = "Setup autoscale."
  default     = "true"
}

variable "autoscale_rpm_enabled" {
  description = "Setup autoscale for RPM."
  default     = "true"
}


variable "service_desired_count" {
  default     = 2
}


variable "autoscale_max_capacity" {
  default     = 10
}


variable "detectron_service_name" {
  default     = "detectron_service_test"
}

variable "alphapose_service_name" {
  default     = "alphapose_service_test"
}

variable "animation_service_name" {
  default     = "animation_service_deploy"
}

variable "sketch_service_name" {
  default     = "sketch_service_test"
}


variable "desired_count" {
  default = 2
}

variable "target_capacity" {
  default = "2"
}

variable "application_name" {
  default = "kids_sketch_animation"
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

variable "primary_hosted_zone" {
  default = ".metademolab.com"
}

variable "primary_hosted_zone_id" {
  default = "Z001431830A482VL9FT2U"
}

#variable "domain_cert" {
#  default = "arn:aws:acm:us-east-1:223420189915:certificate/1009bfac-ea5e-470a-8da5-6c43ed10f886"
#}

variable "detectron_path" {
  default = "/predictions/D2_humanoid_detector"
}

variable "alphapose_path" {
  default = "/predictions/alphapose"
}

variable "animation_path" {
  default = "/generate_animation"
}


variable "detectron_port" {
  default = 5911
}

variable "alphapose_port" {
  default = 5912
}

variable "animation_port" {
  default = 5000
}

variable "sketch_api_port" {
  default = 5000
}

variable "hosted_zone_id"{
  type = string
}

variable "cloudfront_cert_arn"{
  type = string
}

variable "sketch_api_cert_arn"{
  type = string
}

variable "instance_iam_role" {
  type = string
}

variable "beta_instance_iam_role" {
  type = string
}

variable "ami_id" {
  default = "ami-08e0b00e3616220d8"
}

variable "instance_type" {
  default = "c5n.9xlarge"      
}

variable "key_pair" {
  default = "ecs_ec2_instances"
}

variable "api_hosted_zone_id" {
  type = string
}

variable "api_hosted_zone" {
  default = ".metaaidemo.com"
}