
### AWS ALB, Security Groups
resource "aws_lb" "gpu_asg_alb" {
  name               = "gpu-asg-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-0c9000062b58977f0", aws_security_group.gpu_asg_alb_sg.id]
  subnets            = var.subnets

  enable_deletion_protection = false
}

resource "aws_security_group" "gpu_asg_alb_sg" {
  name   = "gpu-alb-sg-${var.environment}"
  vpc_id = local.vpc_id

  ingress {
   protocol         = "tcp"
   from_port        = 80
   to_port          = 80
   cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
   protocol         = -1
   from_port        = 0
   to_port          = 0
   cidr_blocks      = ["0.0.0.0/0"]
  }
}


resource "aws_security_group" "gpu_instance_sg" {
  name   = "gpu-instance-sg-${var.environment}"
  vpc_id = local.vpc_id

  ingress {
   protocol         = -1
   from_port        = 0
   to_port          = 0
   security_groups      = [aws_security_group.gpu_asg_alb_sg.id]
  }


  egress {
   protocol         = -1
   from_port        = 0
   to_port          = 0
   cidr_blocks      = ["0.0.0.0/0"]
  }
}


resource "aws_alb_target_group" "detect_gpu_tg" {
  name        = "detect-gpu-asg-tg"
  port        = 5911
  protocol    = "HTTP"
  vpc_id      = local.vpc_id
  target_type = "instance"


  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "3"
    unhealthy_threshold = "2"
    path                = "/ping"
  }
}

resource "aws_alb_listener" "asg_listener" {
  load_balancer_arn = aws_lb.gpu_asg_alb.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.detect_gpu_tg.arn
  }
}