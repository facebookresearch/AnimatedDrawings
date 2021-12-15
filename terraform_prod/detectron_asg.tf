resource "aws_iam_instance_profile" "detect_ec2_instance_profile" {
  name = "gpu_profile_asg_${var.environment}"
  role = aws_iam_role.detectron_asg_instance_role.name
}

resource "aws_iam_role" "detectron_asg_instance_role" {
  name = "${var.environment}_gpu_instance_role"

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
resource "aws_iam_policy" "detectron_asg_policy" {
  name        = "${var.environment}_detectron_asg_policy"
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

resource "aws_iam_policy_attachment" "ec2_instance-policy-attach" {
  name       = "gpu-asg-policy-attachment-${var.environment}"
  roles      = [aws_iam_role.detectron_asg_instance_role.name]
  policy_arn = aws_iam_policy.detectron_asg_policy.arn
}

resource "aws_iam_policy_attachment" "ec2-container-service" {
  name       = "gpu-asg-policy-attachment-${var.environment}"
  roles      = [aws_iam_role.detectron_asg_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_policy_attachment" "ecr-registy-service" {
  name       = "gpu-asg-registry-${var.environment}"
  roles      = [aws_iam_role.detectron_asg_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}






resource "aws_launch_configuration" "detect_ec2_launch_config" {
  name_prefix                 = var.environment
  image_id                    = var.detectron_ami_id
  instance_type               = var.detectron_instance_type
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.detect_ec2_instance_profile.name
  security_groups             = ["${aws_security_group.ecs_cluster_service_sg.id}"]
  enable_monitoring           = true
  key_name                    = var.detectron_key_pair

  root_block_device {
    volume_size = "500"
    volume_type = "gp3"
  }

  user_data = <<EOF
#!/bin/bash
aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.us-east-2.amazonaws.com
docker run -d --gpus all -p 5911:5911 ${local.account_id}.dkr.ecr.us-east-2.amazonaws.com/detectron_gpu_image_repo_${var.environment}:latest
EOF

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "detect_ec2_ecs_asg" {
  name                      = "detectron-asg-gpu-${var.environment}"
  launch_configuration      = aws_launch_configuration.detect_ec2_launch_config.name
  min_size                  = 1
  max_size                  = 3
  health_check_type         = "EC2"
  health_check_grace_period = 0
  default_cooldown          = 30
  desired_capacity          = 2
  vpc_zone_identifier       = var.subnets == [] ? var.subnets[0].ids : var.subnets
  wait_for_capacity_timeout = "3m"
  target_group_arns         = ["${aws_alb_target_group.detectron_ec2_tg.arn}"]

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Name"
    value               = "DETECTRON-ASG-GPU"
    propagate_at_launch = true
  }

  tag {
    key                 = "prod"
    value               = ""
    propagate_at_launch = true
  }
}

