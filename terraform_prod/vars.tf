variable "region" {
    type        = string
    default = "us-east-2"
}

variable "environment" {
    type        = string
    default = "production"
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
  default     = "detectron_service_prod"
}

variable "alphapose_service_name" {
  default     = "alphapose_service_prod"
}

variable "animation_service_name" {
  default     = "animation_service_prod"
}

variable "sketch_service_name" {
  default     = "sketch_service_prod"
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
  default = "prod-demo-sketch-www.com"
}

variable "model_store_bucket" {
  default = "prod-demo-sketch-in-model-store"
}

variable "interim_bucket" {
  default = "prod-demo-sketch-out-interim-files"
}

variable "consents_bucket" {
  default = "prod-demo-sketch-out-consents"
}

variable "video_bucket" {
  default = "prod-demo-sketch-out-animations"
}

variable "primary_hosted_zone" {
  default = ".metademolab.com"
}

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

variable "remote_state_bucket" {
  default = "sketch-prod-terraform-s3-backend"
}

variable "remote_lock_table" {
  default = "sketch-prod-terraform-s3-backend-locking"
}

variable "video_alias" {
  default = "prod-sketch-video.metademolab.com"
}

variable "sketch_alias" {
  default = "prod-sketch.metademolab.com"
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