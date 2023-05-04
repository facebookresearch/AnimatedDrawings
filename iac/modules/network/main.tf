# vpc
resource "aws_vpc" "main" {
  cidr_block           = var.network.cidr
  enable_dns_hostnames = "true"
  enable_dns_support   = "true"

  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-vpc"
    BillingGroup = var.common.app_name
  }
}

# internet gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-igw"
    BillingGroup = var.common.app_name
  }
}

# subnet
resource "aws_subnet" "main_public" {
  for_each = { for i, s in var.network.public_subnets : i => s }

  vpc_id            = aws_vpc.main.id
  availability_zone = "${var.common.region}${each.value.az}"
  cidr_block        = each.value.cidr

  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-public-${each.key}"
    BillingGroup = var.common.app_name
  }
}

# private
resource "aws_subnet" "main_private" {
  for_each = { for i, s in var.network.private_subnets : i => s }

  vpc_id            = aws_vpc.main.id
  availability_zone = "${var.common.region}${each.value.az}"
  cidr_block        = each.value.cidr

  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-private-${each.key}"
    BillingGroup = var.common.app_name
  }
}

# route table
resource "aws_route_table" "main_public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-public-igw"
    BillingGroup = var.common.app_name
  }
}

resource "aws_route_table" "main_private" {
  for_each = { for i, s in var.network.private_subnets : i => s }

  vpc_id = aws_vpc.main.id
  tags = {
    Name         = "${var.common.env}-${var.common.app_name}-private-${each.key}-nat"
    BillingGroup = var.common.app_name
  }
}

resource "aws_route" "main_private" {
  for_each = { for i, rt in aws_route_table.main_private : i => rt }

  route_table_id         = each.value.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}

# route table association from public to internet gateway
resource "aws_route_table_association" "main_public" {
  for_each = { for i, s in aws_subnet.main_public : i => s }

  route_table_id = aws_route_table.main_public.id
  subnet_id      = each.value.id
}

resource "aws_route_table_association" "main_private" {
  for_each = { for i, s in aws_subnet.main_private : i => s }

  route_table_id = aws_route_table.main_private[each.key].id
  subnet_id      = each.value.id
}
