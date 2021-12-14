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
  value = aws_ecs_cluster.ecs_cluster.name
}
 
output "aws_lb_dns_name" {
  value = aws_lb.ecs_cluster_alb.dns_name
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
  value = "${aws_lb.ecs_cluster_alb.dns_name}:${var.detectron_port}${var.detectron_path}"
}

output "alphapose_model_dns" {
  value = "${aws_lb.ecs_cluster_alb.dns_name}:${var.alphapose_port}${var.alphapose_path}"
}

output "animation_api_dns" {
  value = "${aws_lb.ecs_cluster_alb.dns_name}:${var.animation_port}${var.animation_path}"
} 

output "sketch_api_dns" {
  value = "${aws_lb.ecs_cluster_alb.dns_name}"
} 

output "video_dns" {
  value = "${aws_cloudfront_distribution.video_distribution.domain_name}"
} 
