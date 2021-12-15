output "detectron_ecr" {
  value = aws_ecr_repository.detectron_repo.repository_url
} 

output "animation_ecr" {
  value = aws_ecr_repository.animation_repo.repository_url
}

output "alphapose_ecr" {
  value = aws_ecr_repository.alphapose_repo.repository_url
}

output "sketch_ecr" {
  value = aws_ecr_repository.sketch_repo.repository_url
} 
 
output "devops_role" {
  value = aws_iam_role.devops_role.arn
} 

output "aws_ecs_cluster" {
  value = aws_ecs_cluster.ml_devops_cluster.name
} 
output "aws_lb_dns_name" {
  value = aws_lb.ml_devops_alb.dns_name
} 
output "aws_alb_target_group" {
  value = aws_alb_target_group.detectron_tg.arn
} 

output "detectron_container_name" {
  value = var.detectron_container_name
}

output "alphapose_container_name" {
  value = var.alphapose_container_name
}

output "animation_container_name" {
  value = var.animation_container_name
}

output "sketch_container_name" {
  value = var.sketch_container_name
}

output "detectron_model_dns" {
  value = "${aws_lb.ml_devops_alb.dns_name}/predictions/D2_humanoid_detector"
}

output "alphapose_model_dns" {
  value = "${aws_lb.ml_devops_alb.dns_name}:5912/predictions/alphapose"
}

output "animation_api_dns" {
  value = "${aws_lb.ml_devops_alb.dns_name}:5000/generate_animation"
} 

output "sketch_api_dns" {
  value = "${aws_lb.ml_devops_alb.dns_name}"
} 

data "aws_vpc" "default" {
  default = true
}

output "vpc_id" {
  value = "${data.aws_vpc.default.id}"
}
