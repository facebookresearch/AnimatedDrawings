data "aws_ami" "amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn-ami*amazon-ecs-optimized"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["amazon", "self"]
}

data "aws_subnet_ids" "subnets" {
  count  = var.subnets == [] ? 1 : 0
  vpc_id = var.vpc_id
}


resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "ecs_ec2_profile_${var.environment}"
  role = aws_iam_role.ec2_instance_role.name
}

resource "aws_iam_role" "ec2_instance_role" {
  name = "ecs_cluster_instance_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs.amazonaws.com"
        }
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "batch.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
    ]
  })

}

## TASK ROLE POLICY
resource "aws_iam_policy" "ec2_instance_policy" {
  name        = "ecs_ec2_instance_policy"
  description = "Necessary DevOps Permissions for Maintenance and Testing. ECS Full Access is needed to maintain, test, monitor Fargate Clusters"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ec2:*",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "s3:ListBucket",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ],
        Effect   = "Allow",
        Resource = "*",
      },
      {
        Action = [
          "ecs:*",
        ],
        Effect   = "Allow",
        Resource = "*",
    }]
  })
}

resource "aws_iam_policy_attachment" "detectron_attach" {
  name       = "detectron"
  roles      = [aws_iam_role.ec2_instance_role.name]
  policy_arn = aws_iam_policy.ec2_instance_policy.arn
}

resource "aws_iam_policy_attachment" "detectron_container_service" {
  name       = "detectron-containerservice-policy-attachment"
  roles      = [aws_iam_role.ec2_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}




resource "aws_launch_configuration" "detectron_launch_config" {
  name_prefix                 = "detectron"
  image_id                    = var.ami_id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name
  security_groups             = ["sg-0e15f3169ff2af367"]
  enable_monitoring           = true
  key_name                    = "detectron-ecs-key"

  root_block_device {
    volume_size = "500"
    volume_type = "gp3"
  }

  user_data = <<EOF
#! /bin/bash
sudo apt-get update
sudo echo "ECS_CLUSTER=${aws_ecs_cluster.ml_devops_cluster.name}" >> /etc/ecs/ecs.config
sudo echo "ECS_ENABLE_GPU_SUPPORT=true" >> /etc/ecs/ecs.config
sudo echo "ECS_NVIDIA_RUNTIME=nvidia" >> /etc/ecs/ecs.config
sudo echo "ECS_DATADIR=/data" >> /etc/ecs/ecs.config
sudo echo "ECS_ENABLE_AWSLOGS_EXECUTIONROLE_OVERRIDE=true" >> /etc/ecs/ecs.config
sudo echo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
sudo echo ECS_AVAILABLE_LOGGING_DRIVERS='["json-file","syslog","awslogs","none"]' >> /etc/ecs/ecs.config
sudo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_ecs_capacity_provider" "detectron_ecs_cp" {
  name = "detectron_ec2_cluster_capacity_${var.environment}"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.detectron_asg.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 1
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
}

resource "aws_autoscaling_group" "detectron_asg" {
  name                      = "detectron_ec2_cluster_asg_${var.environment}"
  launch_configuration      = aws_launch_configuration.detectron_launch_config.name
  min_size                  = var.target_capacity
  max_size                  = var.target_capacity * 2
  health_check_type         = "EC2"
  health_check_grace_period = 0
  default_cooldown          = 30
  desired_capacity          = var.target_capacity
  vpc_zone_identifier       = var.subnets == [] ? data.aws_subnet_ids.subnets[0].ids : var.subnets
  wait_for_capacity_timeout = "3m"


  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Name"
    value               = "detectron_asg"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }


}

############### DETECTRON ECS-EC2 SERVICE
## NEW MODEL TEMPLATE
resource "aws_alb_target_group" "detect_ec2_tg" {
  name        = "Detctron-EC2-TG-${var.environment}"
  port        = 5911
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"


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

resource "aws_alb_listener" "detect_ec2_listener" {
  load_balancer_arn = aws_lb.ml_devops_alb.arn
  port              = 5555
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detect_ec2_tg.arn
  }
}

resource "aws_security_group" "detect_ec2_sg" {
  name   = "ECS-CLUSTER-${var.environment}-sg"
  vpc_id = var.vpc_id

  ingress {
    protocol        = -1
    from_port       = 0
    to_port         = 0
    security_groups = "${aws_lb.ml_devops_alb.security_groups}"

  }

  ingress {
    protocol        = "tcp"
    from_port       = 22
    to_port         = 22
    cidr_blocks = ["0.0.0.0/0"]

  }


  egress {
    protocol    = -1
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_ecs_service" "detect_ec2_service" {
  name            = "${var.detect_ec2_service_name}"
  launch_type     = "EC2"
  cluster         = aws_ecs_cluster.ml_devops_cluster.id
  task_definition = aws_ecs_task_definition.detect_ec2_task_definition.arn
  desired_count   = 1

  load_balancer {
    target_group_arn = aws_alb_target_group.detect_ec2_tg.arn
    container_name   = "${var.detectron_container_name}"
    container_port   = 5911
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

}
resource "aws_cloudwatch_log_group" "ecs_ec2_log_group" {
  name = "/ecs/EC2_CLUSTER-${var.environment}"
}


resource "aws_ecs_task_definition" "detect_ec2_task_definition" {
  family                   = "Detect_LT_Deploy_TF"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "2 vCPU"
  memory                   = "5GB"
  task_role_arn            = aws_iam_role.devops_role.arn

  container_definitions = jsonencode([
    {
      "name"      = "${var.detectron_container_name}"
      "image"     = "${var.detectron_image}"
      "essential" = true
      "portMappings" = [
        {
          "containerPort" = 5911
          "hostPort"      = 5911
        }
      ]
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-region": "us-east-2",
          "awslogs-group": "${aws_cloudwatch_log_group.ecs_ec2_log_group.name}",
          "awslogs-create-group": "true",
          "awslogs-stream-prefix": "DETECTRON"
        }
      }

    }
  ])
}
