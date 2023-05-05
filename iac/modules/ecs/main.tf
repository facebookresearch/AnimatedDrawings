resource "aws_ecs_cluster" "main" {
  name = "${var.common.env}-${var.common.app_name}-ecs-cluster"
  tags = {
    Name         = var.common.app_name
    BillingGroup = var.common.app_name
  }
}
