## ANIMATION API TARGET GROUP / HEALTH CHECK/ PORT CONFIGURATION
resource "aws_alb_target_group" "animation_tg" {
  name        = "animation-tg-${var.environment}"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "ip"


  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "3"
    unhealthy_threshold = "2"
    path                = "/healthy"
  }
}

resource "aws_alb_listener" "animation_listener" {
  load_balancer_arn = aws_lb.ecs_cluster_alb.id
  port              = 5000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.animation_tg.arn
  }
}




#ALPHAPOSE ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "animation_ecs_service" {
  name        = "${var.animation_service_name}-env"
  launch_type = "FARGATE"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.animation_task_definition.arn
  desired_count   = var.desired_count
  deployment_minimum_healthy_percent = 2

  network_configuration {
      security_groups  = var.security_groups
      subnets          = var.subnets
      assign_public_ip = true
    }

  load_balancer {
    target_group_arn = aws_alb_target_group.animation_tg.arn
    container_name   = var.animation_container_name
    container_port   = 5000
  }

  lifecycle {
   ignore_changes = [task_definition]
 }

}


resource "aws_ecs_task_definition" "animation_task_definition" {
  family = "animation-td-env"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 4096
  memory                   = 30720
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.devops_role.arn
  

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
      "environment": [
                {
                    "name": "AWS_S3_INTERIM_BUCKET",
                    "value": "${aws_s3_bucket.interim.id}"
                },
                {
                    "name": "AWS_S3_CONSENTS_BUCKET",
                    "value": "${aws_s3_bucket.consents.id}"
                },
                {
                    "name": "AWS_S3_VIDEOS_BUCKET",
                    "value": "${aws_s3_bucket.video.id}"
                },
                {
                    "name": "USE_AWS",
                    "value": "1"
                }
            ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "us-east-2",
          "awslogs-group": "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-create-group": "true",
          "awslogs-stream-prefix": "${var.animation_container_name}-logs"
        }
      }

    }
  ])
}


#ANIMATION AUTOSCALING

resource "aws_appautoscaling_target" "animation_asg_target" {
  max_capacity = 10
  min_capacity = 2
  resource_id = "service/${aws_ecs_cluster.ecs_cluster.name}/${aws_ecs_service.animation_ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

resource "aws_appautoscaling_policy" "animation_requests" {
  name               = "animation_requets_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 1000
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.ecs_cluster_alb.arn_suffix}/${aws_alb_target_group.animation_tg.arn_suffix}"
    }
  }
}

resource "aws_appautoscaling_policy" "animation_memory" {
  name               = "animation_memory_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value       = 80
  }
}

resource "aws_appautoscaling_policy" "animation_cpu" {
  name = "animation_cpu_policy"
  policy_type = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 60
  }
}
