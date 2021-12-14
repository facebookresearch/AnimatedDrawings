## NEW MODEL TEMPLATE
resource "aws_alb_target_group" "detectron_ec2_tg" {
  name        = "detectron-ec2-tg-${var.environment}"
  port        = 5911
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance"


  health_check {
    healthy_threshold   = "2"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "3"
    unhealthy_threshold = "3"
    path                = "/ping"
  }
}

resource "aws_alb_listener" "detectron_http" {
  load_balancer_arn = aws_lb.ec2_cluster_alb.arn
  port              = 5911
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detectron_ec2_tg.arn
  }
}


resource "aws_route53_record" "detectron_ec2" {
  zone_id = var.primary_hosted_zone_id
  name    = "detect-gpu-api${var.primary_hosted_zone}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.ec2_cluster_alb.dns_name]
}


#ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "detectron_ec2_service" {
  name        = "${var.detectron_service_name}_ec2_gpu_test"
  launch_type = "EC2"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.detect_ec2_task_definition.arn
  desired_count   = var.desired_count
  deployment_minimum_healthy_percent = 2

  load_balancer {
    target_group_arn = aws_alb_target_group.detectron_ec2_tg.arn
    container_name   = var.detectron_container_name
    container_port   = 5911
  }


  lifecycle {
   ignore_changes = [task_definition]
 }

}


resource "aws_ecs_task_definition" "detect_ec2_task_definition" {
  family                   = "detect_ec2_gpu"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "5 vCPU"
  memory                   = "3GB"
  #execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.devops_role.arn

  container_definitions = jsonencode([
    {
      "name"      = "${var.detectron_container_name}"
      "image"     = "${aws_ecr_repository.detectron_repo.repository_url}:latest"
      "essential" = true
      "portMappings" = [
        {
          "containerPort" = 5911
          "hostPort"      = 5911
        }
      ]
      "resourceRequirements" = [
        {
          "type" : "GPU",
          "value" : "1"
        }
      ]
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "us-east-2",
          "awslogs-group": "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-create-group": "true",
          "awslogs-stream-prefix": "${var.detectron_container_name}-logs"
        }
    
    }
    }
  ])
}
