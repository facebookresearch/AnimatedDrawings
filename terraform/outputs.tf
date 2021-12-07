output "detectron_ecr_arn" {
  value = aws_ecr_repository.detectron_repo.arn
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