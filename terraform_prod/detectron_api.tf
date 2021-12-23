## NEW MODEL TEMPLATE
resource "aws_alb_target_group" "detectron_ec2_tg" {
  name        = "detectron-ecs-${var.environment}-tg"
  port        = 5911
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance"


  health_check {
    healthy_threshold   = "2"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "5"
    unhealthy_threshold = "5"
    path                = "/ping"
  }
}

resource "aws_alb_listener" "detectron_http" {
  load_balancer_arn = aws_lb.detectron_ecs_alb.arn
  port              = 5911
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detectron_ec2_tg.arn
  }
}



#ECS SERVICE AND TASK DEFINITION
resource "aws_ecs_service" "detectron_ec2_service" {
  name                               = "detectron_service-${var.environment}"
  launch_type                        = "EC2"
  cluster                            = aws_ecs_cluster.ecs_cluster.id
  task_definition                    = aws_ecs_task_definition.detect_ec2_task_definition.arn
  desired_count                      = 2
  deployment_minimum_healthy_percent = 2
  force_new_deployment = true

  placement_constraints {
    type       = "memberOf"
    expression = "attribute:ecs.instance-type  == g4dn.2xlarge"
  }


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
  family                   = "detectron_task_definition-${var.environment}"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "5 vCPU"
  memory                   = "3GB"
  task_role_arn = aws_iam_role.devops_role.arn

  container_definitions = jsonencode([
    {
      "name"      = "${var.detectron_container_name}"
      "image"     = "${aws_ecr_repository.detectron_gpu_repo.repository_url}:latest"
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
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-region" : "us-east-2",
          "awslogs-group" : "${aws_cloudwatch_log_group.log_group.name}",
          "awslogs-create-group" : "true",
          "awslogs-stream-prefix" : "${var.detectron_container_name}-logs"
        },
        "placementConstraints" : [
          {
            "expression" : "attribute:ecs.instance-type == g4dn.2xlarge",
            "type" : "memberOf"
        }]
      }
    }
  ])
}
