# module "ecs_service_sg" {
#   source          = "terraform-aws-modules/security-group/aws"
#   name            = "${var.common.app_name}-sg"
#   use_name_prefix = false
#   vpc_id          = var.network.vpc_id

#   egress_with_cidr_blocks              = each.value.security_group.egress_rules
#   egress_with_source_security_group_id = each.value.security_group.egress_rules_security_group_id

#   tags = {
#     Name         = "${var.common.app_name}-sg"
#     BillingGroup = var.common.app_name
#   }
# }

data "aws_iam_role" "ex" {
  name = "ecsTaskExecutionRole"
}

# data "aws_iam_role" "app" {
#   name = "${var.common.env}-${var.common.app_name}-ecsTaskInstanceRole"
# }

resource "aws_ecs_task_definition" "main" {
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  family                   = var.task.family
  cpu                      = var.task.cpu
  memory                   = var.task.memory
  container_definitions    = jsonencode(var.task.container_definitions)
  execution_role_arn       = data.aws_iam_role.ex.arn
  # task_role_arn            = data.aws_iam_role.app.arn

  runtime_platform {
    operating_system_family = "LINUX"
  }
  tags = {
    Name         = var.common.app_name
    BillingGroup = var.common.app_name
  }
}

resource "aws_ecs_service" "main" {
  name                   = "${var.common.env}-${var.common.app_name}-ecs-service"
  launch_type            = "FARGATE"
  platform_version       = "latest"
  cluster                = aws_ecs_cluster.main.id
  task_definition        = aws_ecs_task_definition.main.arn
  desired_count          = 1
  enable_execute_command = true
  force_new_deployment   = true

  network_configuration {
    subnets          = var.network.private_subnet_ids
    assign_public_ip = false
    # security_groups  = [module.ecs_service_sg[each.key].security_group_id]
  }

  lifecycle {
    ignore_changes = [
      task_definition
    ]
  }

  tags = {
    Name         = var.common.app_name
    BillingGroup = var.common.app_name
  }
}
