resource "aws_ecr_repository" "main" {
  name = "${var.common.env}-${var.common.app_name}-ecr"
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-ecr"
    BillingGroup = var.common.app_name
  }
}
