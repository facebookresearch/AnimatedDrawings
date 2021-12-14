resource "aws_ecr_repository" "detectron_gpu_repo" {
  name                 = "detectron_gpu_image_repo_${var.environment}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    env = "model-testing"
  }

}

resource "aws_ecr_repository_policy" "detectron_gpu_ecr_policy" {
  repository = aws_ecr_repository.detectron_gpu_repo.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowPushPull",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : [
            "${var.sketch_instance_arn}",
            "${aws_iam_role.detectron_asg_instance_role.arn}" #GPU IAM ROLE
          ]
        },
        "Action" : [
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:CompleteLayerUpload",
          "ecr:GetDownloadUrlForLayer",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
          "ecr:GetAuthorizationToken"
        ]
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "detectron_gpu_lifecycle_polcy" {
  repository = aws_ecr_repository.detectron_gpu_repo.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "keep last 10 images"
      action = {
        type = "expire"
      }
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
    }]
  })
}