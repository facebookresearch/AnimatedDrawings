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
  load_balancer_arn = aws_lb.ecs_cluster_alb.id
  port              = 5000
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.animation_ec2_tg.arn
  }
}



resource "aws_ecs_service" "animation_ec2_service" {
  name            = "animation_service_deploy"
  launch_type     = "EC2"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.animation_ec2_task_definition.arn
  desired_count   = 3
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
  family                   = "animation_task_def"
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
          "value" : "33"
        },
        {
          "name" : "ANIMATE_WSGI_THREADS",
          "value" : "1"
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
