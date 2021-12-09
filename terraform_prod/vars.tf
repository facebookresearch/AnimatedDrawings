variable "region" {
    type        = string
    default = "us-east-2"
}

variable "environment" {
    type        = string
    default = "beta"
}

variable "sketch_instance_arn" {
    type        = string
    default = "arn:aws:iam::223420189915:role/ML_DEVOPS_INSTANCE_ROLE"
}


variable "subnets" {
    default = ["subnet-013b1eb85e4031acb", "subnet-0ddd0fb00120f41be", "subnet-0d1bc39cf316080a1"]
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
  default     = "animation_service_test"
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
  default = "beta-test-demo-sketch-www.com"
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
