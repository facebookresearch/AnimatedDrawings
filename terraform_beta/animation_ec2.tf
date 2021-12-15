## NEW MODEL TEMPLATE
resource "aws_alb_target_group" "animation_ec2_tg" {
  name        = "animation-ec2-tg-${var.environment}"
  port        = 5000
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
    path                = "/healthy"
  }
}

resource "aws_alb_listener" "http_ec2" {
  load_balancer_arn = aws_lb.ec2_cluster_alb.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.animation_ec2_tg.arn
  }
}

resource "aws_route53_record" "animation" {
  zone_id = var.primary_hosted_zone_id
  name    = "detectron-gpu-API${var.primary_hosted_zone}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.ec2_cluster_alb.dns_name]
}


resource "aws_ecs_service" "animation_ec2_service" {
  name            = "ani_ec2_deploy"
  launch_type     = "EC2"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.animation_ec2_task_definition.arn
  desired_count   = 1

  load_balancer {
    target_group_arn = aws_alb_target_group.animation_ec2_tg.arn
    container_name   = var.animation_container_name
    container_port   = 5000
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

}
resource "aws_cloudwatch_log_group" "beta_ec2_log_group" {
  name = "/ecs/${var.environment}-ec2-ecs-animation"
}


resource "aws_ecs_task_definition" "animation_ec2_task_definition" {
  family                   = "ani_ec2_task_deploy"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "2 vCPU"
  memory                   = "5GB"
  task_role_arn            = aws_iam_role.devops_role.arn
  execution_role_arn       = aws_iam_role.task_execution_role.arn

  container_definitions = jsonencode([
    {
      "name"      = "${var.animation_container_name}"
      "image"     = "${aws_ecr_repository.animation_repo.repository_url}:latest"
      "essential" = true
      "portMappings" = [
        {
          "containerPort" = 5000
          "hostPort"      = 5000
        }
      ]
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-region" : "${var.region}",
          "awslogs-group" : "${aws_cloudwatch_log_group.beta_ec2_log_group.name}",
          "awslogs-stream-prefix" : "${var.animation_container_name}-logs",
          "awslogs-create-group": "true"
        }
      }

    }
  ])
}
