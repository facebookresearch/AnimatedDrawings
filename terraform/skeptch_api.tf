## SKETCH API TARGET GROUP / HEALTH CHECK/ PORT CONFIGURATION

resource "aws_alb_target_group" "sketch_tg" {
  name        = "SKETCH-FARGATE-TG-${var.environment}"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
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
  load_balancer_arn = aws_lb.ml_devops_alb.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.sketch_tg.arn
  }
}




#ALPHAPOSE ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "sketch_ecs_service" {
  name        = "${var.sketch_service_name}-Deploy-Test-UPDATE"
  launch_type = "FARGATE"
  cluster         = aws_ecs_cluster.ml_devops_cluster.id
  task_definition = aws_ecs_task_definition.sketch_task_definition.arn
  desired_count   = 4
  deployment_minimum_healthy_percent = 2

  network_configuration {
      security_groups  = var.security_groups
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
  family = "sketch-taskdefinition"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 4096
  memory                   = 30720
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.devops_role.arn
  

  container_definitions = jsonencode([
    {
      "name"      = "${var.sketch_container_name}"
      "image"     = "${var.sketch_image}"
      "essential" = true
      "portMappings" = [
        {
          "containerPort" = 5000
          "hostPort"      = 5000
        }
      ]
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "us-east-2",
          "awslogs-group": "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-create-group": "true",
          "awslogs-stream-prefix": "${var.sketch_container_name}-logs"
        }
      }

    }
  ])
}


#SKETCH AUTOSCALING

resource "aws_appautoscaling_target" "sketch_asg_target" {
  max_capacity = 10
  min_capacity = 5
  resource_id = "service/${aws_ecs_cluster.ml_devops_cluster.name}/${aws_ecs_service.sketch_ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

resource "aws_appautoscaling_policy" "sketch_requests" {
  name               = "detectron_requets_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.sketch_asg_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sketch_asg_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sketch_asg_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 1000
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.ml_devops_alb.arn_suffix}/${aws_alb_target_group.sketch_tg.arn_suffix}"
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

    target_value       = 80
  }
}

resource "aws_appautoscaling_policy" "sketch_requests_cpu" {
  name = "detectron_cpu_policy"
  policy_type = "TargetTrackingScaling"
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
