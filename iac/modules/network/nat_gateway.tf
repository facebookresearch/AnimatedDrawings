# elastic ip
resource "aws_eip" "main" {
  vpc = "true"
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-eip"
    BillingGroup = var.common.env
  }
}

# nat
resource "aws_nat_gateway" "main" {
  allocation_id     = aws_eip.main.id
  subnet_id         = aws_subnet.main_public[0].id
  connectivity_type = "public"

  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-nat"
    BillingGroup = var.common.env
  }
}
