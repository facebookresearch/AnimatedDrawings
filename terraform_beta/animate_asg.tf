resource "aws_iam_instance_profile" "ec2_ecs_instance_profile" {
  name = "animation_ecs_cluster_instance_profile-${var.environment}"
  role = aws_iam_role.ec2_ecs_instance_role.name
}

resource "aws_iam_role" "ec2_ecs_instance_role" {
  name = "${var.environment}_animation_ec2_instance_role"

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
      }
    ]
  })

}

## TASK ROLE POLICY
resource "aws_iam_policy" "ec2_ecs_role_policy" {
  name        = "animation_ec2_ecs_policy-${var.environment}"
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
          "ecr:*",
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

resource "aws_iam_policy_attachment" "animation-instance-policy-attach" {
  name       = "animation-ec2-instance-attachment-${var.environment}"
  roles      = [aws_iam_role.ec2_ecs_instance_role.name]
  policy_arn = aws_iam_policy.ec2_ecs_role_policy.arn
}

resource "aws_iam_policy_attachment" "animation-ec2-container-service" {
  name       = "animation-container-instance-attachment"
  roles      = [aws_iam_role.ec2_ecs_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}




resource "aws_launch_configuration" "ec2_launch_config" {
  name_prefix                 = "animation-ecs-ec2-launch-config-${var.environment}"
  image_id                    = var.animation_ami_id
  instance_type               = var.animation_instance_type
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_ecs_instance_profile.name
  security_groups             = ["${aws_security_group.ecs_cluster_service_sg.id}"]
  enable_monitoring           = true
  key_name                    = var.animation_key_pair

  root_block_device {
    volume_size = "500"
    volume_type = "gp3"
  }

  #user_data = "${file("user_data.sh")}"
  user_data = "#!/bin/bash\necho ECS_CLUSTER=${aws_ecs_cluster.ecs_cluster.name} >> /etc/ecs/ecs.config"

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_autoscaling_group" "animation_ec2_ecs_asg" {
  name                      = "animation-ecs-ec2-asg-${var.environment}"
  launch_configuration      = aws_launch_configuration.ec2_launch_config.name
  min_size                  = 5
  max_size                  = 5
  health_check_type         = "EC2"
  health_check_grace_period = 0
  default_cooldown          = 30
  desired_capacity          = 30
  vpc_zone_identifier       = var.subnets == [] ? var.subnets[0].ids : var.subnets
  wait_for_capacity_timeout = "3m"

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Name"
    value               = "${var.environment}-ecs-ec2"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }
}


/*
 * Create CloudWatch alarms to trigger scaling of ASG
 */
resource "aws_cloudwatch_metric_alarm" "animation_scaleUp" {
  alarm_name          = "animation-scaleUp"
  alarm_description   = "ECS cluster scaling metric above threshold"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "Memory_Reservation"
  namespace           = "AWS/ECS"
  statistic           = "Average"
  period              = 300
  #threshold           = var.alarm_threshold_up
  #actions_enabled     = var.alarm_actions_enabled
  #count               = var.alarm_actions_enabled ? 1 : 0
  alarm_actions       = [aws_appautoscaling_policy.animation_memory.arn]
  dimensions = {
    ClusterName = aws_ecs_cluster.ecs_cluster.name
  }
}

resource "aws_cloudwatch_metric_alarm" "animation_scaleDown" {
  alarm_name          = "animation-scaleUp"
  alarm_description   = "ECS cluster scaling metric below threshold"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Memory_Reservarion"
  namespace           = "AWS/ECS"
  statistic           = "Average"
  period              = 300
  #threshold           = var.alarm_threshold_up
  #actions_enabled     = var.alarm_actions_enabled
  #count               = var.alarm_actions_enabled ? 1 : 0
  alarm_actions       = [aws_autoscaling_policy.up.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.ecs_cluster.name
  }
}