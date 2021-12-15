variable "ami_id" {
  default = "ami-0a39b734183d5c064"
}

variable "instance_type" {
  default = "g4dn.2xlarge"
}

variable "environment" {
  default = "loadtest"
}


variable "subnets" {
    default = ["subnet-97fcd7db", "subnet-9daf6ce0", "subnet-d039b3bb"]
}

variable "application_name" {
  default = "detectron_asg_gpu"
}


variable "detectron_gpu_container_name" {
  default = "detectron_asg_gpu"
}

variable "sketch_instance_arn" {
    type        = string
    default = "arn:aws:iam::790537050551:role/iam-role-dev-demo-sketch-out-animations-write"
}

variable "key_pair" {
  default = "detectron-asg-gpu"
}

variable "region" {
  default = "us-east-2"
}


variable "private_hosted_zone_id" {
  type = string
}


variable "primary_dns_name" {
  default = ".dev.metademolab.com"
}