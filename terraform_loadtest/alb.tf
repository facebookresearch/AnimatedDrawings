
### AWS ALB, Security Groups, Subnets
resource "aws_lb" "ecs_cluster_alb" {
  name               = "ecs-cluster-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-0c9000062b58977f0"]
  subnets            = var.subnets

  enable_deletion_protection = false
}

resource "aws_security_group" "ecs_cluster_alb_sg" {
  name   = "ecs-cluster-alb-sg-${var.environment}"
  vpc_id = local.vpc_id

  ingress {
   protocol         = "tcp"
   from_port        = 80
   to_port          = 80
   cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
   protocol         = "tcp"
   from_port        = 443
   to_port          = 443
   cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
   protocol         = "tcp"
   from_port        = 5000
   to_port          = 5000
   cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
   protocol         = "tcp"
   from_port        = 5911
   to_port          = 5911
   cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
   protocol         = "tcp"
   from_port        = 5912
   to_port          = 5912
   cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
   protocol         = "tcp"
   from_port        = 4500
   to_port          = 4500
   cidr_blocks      = ["0.0.0.0/0"]
  }


  egress {
   protocol         = -1
   from_port        = 0
   to_port          = 0
   cidr_blocks      = ["0.0.0.0/0"]
  }
}