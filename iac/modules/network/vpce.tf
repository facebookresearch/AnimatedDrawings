locals {
  interface_endpoints = toset([
    "ecr.dkr",
    "ecr.api",
  ])
  gateway_endpoints = toset([
    "s3"
  ])
}

# vpc endpoint
resource "aws_vpc_endpoint" "interface" {
  for_each = local.interface_endpoints

  service_name        = "com.amazonaws.${var.common.region}.${each.value}"
  vpc_id              = aws_vpc.main.id
  vpc_endpoint_type   = "Interface"
  subnet_ids          = values(aws_subnet.main_private)[*].id
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.vpc_endpoint.id]
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-vpce-${each.value}"
    BillingGroup = var.common.app_name
  }
}

resource "aws_vpc_endpoint" "gateway" {
  for_each = local.gateway_endpoints

  service_name      = "com.amazonaws.${var.common.region}.${each.value}"
  vpc_endpoint_type = "Gateway"
  vpc_id            = aws_vpc.main.id
  route_table_ids   = values(aws_route_table.main_private)[*].id
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-vpce-${each.value}"
    BillingGroup = var.common.app_name
  }
}

# security group
resource "aws_security_group" "vpc_endpoint" {
  name   = "${var.common.env}-${var.common.app_name}-vpc-endpoint"
  vpc_id = aws_vpc.main.id
  lifecycle {
    create_before_destroy = true
  }
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-vpc-endpoint"
    BillingGroup = var.common.app_name
  }
}

resource "aws_security_group_rule" "vpc_endpoint_ingress_https_all" {
  security_group_id = aws_security_group.vpc_endpoint.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "https from anywhere"
}

resource "aws_security_group_rule" "vpc_endpoint_egress_all" {
  security_group_id = aws_security_group.vpc_endpoint.id
  type              = "egress"
  protocol          = "all"
  from_port         = 0
  to_port           = 0
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "all to anywhere"
}
