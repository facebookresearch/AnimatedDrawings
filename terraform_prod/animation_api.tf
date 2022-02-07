## NEW MODEL TEMPLATE
resource "aws_alb_target_group" "animation_ec2_tg" {
  name        = "animation-${var.environment}-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance"


  health_check {
    healthy_threshold   = "2"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "10"
    unhealthy_threshold = "4"
    path                = "/healthy"
  }
}

resource "aws_alb_listener" "http_ec2" {
  load_balancer_arn = aws_lb.animation_ecs_alb.id
  port              = 5000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.animation_ec2_tg.arn
  }
}



resource "aws_ecs_service" "animation_ec2_service" {
  name            = "animation_ecs-${var.environment}"
  launch_type     = "EC2"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.animation_ec2_task_definition.arn
  desired_count   = 10
  force_new_deployment = true

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.instance-type  == c5.4xlarge"
  }
  

  load_balancer {
    target_group_arn = aws_alb_target_group.animation_ec2_tg.arn
    container_name   = var.animation_container_name
    container_port   = 5000
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

}

resource "aws_ecs_task_definition" "animation_ec2_task_definition" {
  family                   = "animation_task_def_memory_${var.environment}"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "10 vCPU"
  memory                   = "10GB"
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
      "environment" : [
        {
          "name" : "AWS_S3_INTERIM_BUCKET",
          "value" : "${aws_s3_bucket.interim.id}"
        },
        {
          "name" : "AWS_S3_CONSENTS_BUCKET",
          "value" : "${aws_s3_bucket.consents.id}"
        },
        {
          "name" : "AWS_S3_VIDEOS_BUCKET",
          "value" : "${aws_s3_bucket.video.id}"
        },
        {
          "name" : "ANIMATE_WSGI_WORKERS",
          "value" : "16"
        },
        {
          "name" : "ANIMATE_WSGI_THREADS",
          "value" : "2"
        },
        {
          "name" : "USE_AWS",
          "value" : "1"
        }
      ],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-region" : "${var.region}",
          "awslogs-group" : "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-stream-prefix" : "${var.animation_container_name}-logs",
          "awslogs-create-group" : "true"
        }
      }
      "placementConstraints" : [
          {
            "expression" : "attribute:ecs.instance-type  == c5.4xlarge",
            "type" : "memberOf"
        }]

    }
  ])
}


/* resource "aws_ecs_capacity_provider" "animation_capacity_provider" {
  name = "animation_cp_${var.environment}"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.animation_ec2_ecs_asg.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      maximum_scaling_step_size = 10
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
} */


#ANIMATION AUTOSCALING

resource "aws_appautoscaling_target" "animation_target" {
  max_capacity       = 15
  min_capacity       = 10
  resource_id        = "service/${aws_ecs_cluster.ecs_cluster.name}/${aws_ecs_service.animation_ec2_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "animation_requests" {
  name               = "animation_requests_policy_${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 66
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.animation_ecs_alb.arn_suffix}/${aws_alb_target_group.animation_ec2_tg.arn_suffix}"
    }
  }
}

resource "aws_appautoscaling_policy" "animation_memory" {
  name               = "animation_memory_policy_${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value = 80
  }
}

resource "aws_appautoscaling_policy" "animation_cpu" {
  name               = "animation_cpu_policy_${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.animation_target.resource_id
  scalable_dimension = aws_appautoscaling_target.animation_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.animation_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 60
  }
}
