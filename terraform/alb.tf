
### AWS ALB 
resource "aws_lb" "ml_devops_alb" {
  name               = "ml-devops-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-0c9000062b58977f0"]
  subnets            = var.subnets

  enable_deletion_protection = false
}