## SKETCH API TARGET GROUP / HEALTH CHECK/ PORT CONFIGURATION

resource "aws_alb_target_group" "sketch_tg" {
  name        = "sketch-api-tg-${var.environment}"
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

resource "aws_alb_listener" "sketch_listener" {
  load_balancer_arn = aws_lb.sketch_public_loadbalancer.id
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.sketch_api_cert_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.sketch_tg.arn
  }
}

resource "aws_lb" "sketch_public_loadbalancer" {
  name               = "sketch-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_cluster_alb_sg.id]
  subnets            = var.subnets

  enable_deletion_protection = false
}

#SKETCH ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "sketch_ecs_service" {
  name                               = var.sketch_service_name
  launch_type                        = "FARGATE"
  cluster                            = aws_ecs_cluster.ecs_cluster.id
  task_definition                    = aws_ecs_task_definition.sketch_task_definition.arn
  desired_count                      = 30
  deployment_minimum_healthy_percent = 2

  force_new_deployment = true

    network_configuration {
    security_groups  = [aws_security_group.ecs_cluster_alb_sg.id]
    subnets          = var.subnets
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.sketch_tg.arn
    container_name   = var.sketch_container_name
    container_port   = 5000
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

}


resource "aws_ecs_task_definition" "sketch_task_definition" {
  family                   = "sketch-api-task-definition-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 4096
  memory                   = 8192
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.devops_role.arn


  container_definitions = jsonencode([
    {
      "name"      = "${var.sketch_container_name}"
      "image"     = "${aws_ecr_repository.sketch_repo.repository_url}:latest"
      "essential" = true
      "portMappings" = [
        {
          "containerPort" = 5000
          "hostPort"      = 5000
        }
      ]
      "environment" : [
        {
          "name" : "ENABLE_UPLOAD",
          "value" : "1"
        },
        {
          "name" : "DETECTRON2_ENDPOINT",
          "value" : "http://${aws_lb.detectron_ecs_alb.dns_name}:5911/predictions/D2_humanoid_detector"
        },
        {
          "name" : "ALPHAPOSE_ENDPOINT",
          "value" : "http://${aws_lb.alphapose_ecs_alb.dns_name}:5912/predictions/alphapose"
        },
        {
          "name" : "ANIMATION_ENDPOINT",
          "value" : "http://${aws_lb.animation_ecs_alb.dns_name}:5000/generate_animation"
        },
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
          "name" : "SKETCH_API_WSGI_WORKERS",
          "value" : "9"
        },
        {
          "name" : "SKETCH_API_WSGI_THREADS",
          "value" : "16"
        },
        {
          "name" : "USE_AWS",
          "value" : "1"
        },
      ],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-region" : "us-east-2",
          "awslogs-group" : "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-create-group" : "true",
          "awslogs-stream-prefix" : "${var.sketch_container_name}-logs"
        }
      }

    }
  ])
}


#ASG SKETCH FARGATE

resource "aws_appautoscaling_target" "sketch_asg_target" {
  max_capacity       = 30
  min_capacity       = 10
  resource_id        = "service/${aws_ecs_cluster.ecs_cluster.name}/${aws_ecs_service.sketch_ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "sketch_requests" {
  name               = "alpahpose_requests_policy-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.sketch_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sketch_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sketch_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 120
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.sketch_public_loadbalancer.arn_suffix}/${aws_alb_target_group.sketch_tg.arn_suffix}"
    }
  }
}

resource "aws_appautoscaling_policy" "sketch_requests_memory" {
  name               = "detectron_memory_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.sketch_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sketch_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sketch_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value = 80
  }
}

resource "aws_appautoscaling_policy" "sketch_requests_cpu" {
  name               = "detectron_cpu_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.sketch_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sketch_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sketch_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 60
  }
}
