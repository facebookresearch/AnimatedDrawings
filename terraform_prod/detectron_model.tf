## DETECRON MODEL TARGET GROUP / HEALTH CHECK/ PORT CONFIGURATION
resource "aws_alb_target_group" "detectron_tg" {
  name        = "detectron-tg-${var.environment}"
  port        = 5911
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
    path                = "/ping"
  }
}

resource "aws_alb_listener" "http" {
  load_balancer_arn = aws_lb.ecs_cluster_alb.id
  port              = 5911
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detectron_tg.arn
  }
}

resource "aws_alb_target_group" "detectron_management_tg" {
  name        = "detectron-mgmt-tg-${var.environment}"
  port        = 4500
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
    path                = "/models"
  }
}

resource "aws_alb_listener" "detectron_management_listener" {
  load_balancer_arn = aws_lb.ecs_cluster_alb.id
  port              = 4500
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detectron_management_tg.arn
  }
}



#ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "detectron_ecs_service" {
  name        = "${var.detectron_service_name}-${var.environment}-deploy"
  launch_type = "FARGATE"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.detectron_task_definition.arn
  desired_count   = var.desired_count
  deployment_minimum_healthy_percent = 2

  network_configuration {
      security_groups  = [aws_security_group.ecs_cluster_alb_sg.id, aws_security_group.ecs_cluster_service_sg.id]
      subnets          = var.subnets
      assign_public_ip = true
    }

  load_balancer {
    target_group_arn = aws_alb_target_group.detectron_tg.arn
    container_name   = var.detectron_container_name
    container_port   = 5911
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.detectron_management_tg.arn
    container_name   = var.detectron_container_name
    container_port   = 4500
  }

  lifecycle {
   ignore_changes = [task_definition]
 }

}
resource "aws_cloudwatch_log_group" "log_group" {
  name = "/ecs/FARGATE-CLUSTER-${var.environment}"
}


resource "aws_ecs_task_definition" "detectron_task_definition" {
  family = "detectron_td"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 4096
  memory                   = 30720
  execution_role_arn       = aws_iam_role.task_execution_role.arn
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
        },
        {
          "containerPort" = 4500
          "hostPort"      = 4500
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


#DETECTRON AUTOSCALING

resource "aws_appautoscaling_target" "detect_target" {
  max_capacity = 10
  min_capacity = 2
  resource_id = "service/${aws_ecs_cluster.ecs_cluster.name}/${aws_ecs_service.detectron_ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

resource "aws_appautoscaling_policy" "requests" {
  name               = "detectron_requets_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 1000
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.ecs_cluster_alb.arn_suffix}/${aws_alb_target_group.detectron_tg.arn_suffix}"
    }
  }
}

resource "aws_appautoscaling_policy" "memory" {
  name               = "detectron_memory_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value       = 80
  }
}

resource "aws_appautoscaling_policy" "cpu" {
  name = "detectron_cpu_policy"
  policy_type = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 60
  }
}