output "detectron_gpu_container_name" {
  value = var.detectron_gpu_container_name
}


output "detectron_gpu_ecr" {
  value = aws_ecr_repository.detectron_gpu_repo.repository_url
} 
 