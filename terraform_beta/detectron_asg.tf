resource "aws_iam_instance_profile" "gpu_ecs_instance_profile" {
  name = "gpu_profile-${var.environment}"
  role = aws_iam_role.gpu_ecs_instance_role.name
}

resource "aws_iam_role" "gpu_ecs_instance_role" {
  name = "${var.environment}_detectron_gpu_instance_role"

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
resource "aws_iam_policy" "gpu_policy" {
  name        = "${var.environment}_gpu_policy"
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

resource "aws_iam_policy_attachment" "gpu-instance-policy-attach" {
  name       = "gpu_instance-policy-attachment"
  roles      = [aws_iam_role.gpu_ecs_instance_role.name]
  policy_arn = aws_iam_policy.gpu_policy.arn
}

resource "aws_iam_policy_attachment" "gpu-container-service" {
  name       = "gpu-container-service-policy-attachment"
  roles      = [aws_iam_role.gpu_ecs_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_policy_attachment" "ecr-registy-service" {
  name       = "gpu-asg-registry-${var.environment}"
  roles      = [aws_iam_role.gpu_ecs_instance_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

resource "aws_iam_policy_attachment" "detectron_task_policy_attach" {
  name  = "task_execution-policy-attachment"
  roles = [aws_iam_role.gpu_ecs_instance_role.name]

  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/EC2InstanceProfileForImageBuilderECRContainerBuilds",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchAgentAdminPolicy",
    "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
  ])

  policy_arn = each.value

}



resource "aws_launch_configuration" "gpu_launch_config" {
  name_prefix                 = "detectron-gpu-${var.environment}"
  image_id                    = "ami-0a39b734183d5c064" 
  instance_type               = var.detectron_instance_type
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.gpu_ecs_instance_profile.name
  security_groups             = ["${aws_security_group.ecs_cluster_service_sg.id}"]
  enable_monitoring           = true
  key_name                    = var.detectron_key_pair

  root_block_device {
    volume_size = "500"
    volume_type = "gp3"
  }

  user_data = file("user_data.sh")

  lifecycle {
    create_before_destroy = true
  }
}

/* resource "aws_ecs_capacity_provider" "detectron_ecs_cp" {
  name = "detectron-${var.environment}"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.detect_gpu_ecs_asg.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 1
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
} */

resource "aws_autoscaling_group" "detect_gpu_ecs_asg" {
  name                      = "detectron-ec2-gpu-${var.environment}"
  launch_configuration      = aws_launch_configuration.gpu_launch_config.name
  min_size                  = 2
  max_size                  = 3
  health_check_type         = "EC2"
  health_check_grace_period = 0
  default_cooldown          = 30
  desired_capacity          = 2
  vpc_zone_identifier       = var.subnets == [] ? var.subnets[0].ids : var.subnets
  wait_for_capacity_timeout = "3m"
  target_group_arns         = ["${aws_alb_target_group.detect_gpu_tg.arn}"]

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Name"
    value               = "detectron-ecs-ec2"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }
}

resource "aws_appautoscaling_target" "detect_gpu_target" {
  max_capacity       = 3
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.ecs_cluster.name}/${aws_ecs_service.detectron_ec2_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "gpu_requests" {
  name               = "detectron_requets_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_gpu_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_gpu_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_gpu_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 2000
    disable_scale_in   = false
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.detectron_ecs_alb.arn_suffix}/${aws_alb_target_group.detectron_ec2_tg.arn_suffix}"
    }
  }
}


resource "aws_appautoscaling_policy" "gpu_memory" {
  name               = "detectron_memory_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_gpu_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_gpu_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_gpu_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    target_value = 80
  }
}

resource "aws_appautoscaling_policy" "gpu_cpu" {
  name               = "detectron_cpu_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.detect_gpu_target.resource_id
  scalable_dimension = aws_appautoscaling_target.detect_gpu_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.detect_gpu_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    target_value = 60
  }
}
