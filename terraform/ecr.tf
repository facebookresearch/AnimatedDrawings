
#DETECTRON ECR REPO
resource "aws_ecr_repository" "detectron_repo" {
  name                 = "detectron_image_repo_qa"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    env = "model-testing"
  }

}

resource "aws_ecr_repository_policy" "detectron-ecr-policy" {
  repository = aws_ecr_repository.detectron_repo.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowPushPull",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : [
            "${aws_iam_role.devops_role.arn}",         #TASK EXECUTION IAM ROLE
            "${aws_iam_role.task_execution_role.arn}", #ML_DEVOPS IAM ROLE
            "${var.sketch_instance_arn}"
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

resource "aws_ecr_lifecycle_policy" "detectron_lifecycle_polcy" {
  repository = aws_ecr_repository.detectron_repo.name

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


#ALPHAPOSE ECR REPO
resource "aws_ecr_repository" "alphapose_repo" {
  name                 = "alphapose_image_repo_qa"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    env = "model-testing"
  }

}

resource "aws_ecr_repository_policy" "alphapose-ecr-policy" {
  repository = aws_ecr_repository.alphapose_repo.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowPushPull",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : [
            "${aws_iam_role.devops_role.arn}",         #TASK EXECUTION IAM ROLE
            "${aws_iam_role.task_execution_role.arn}", #ML_DEVOPS IAM ROLE
            "${var.sketch_instance_arn}"
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

resource "aws_ecr_lifecycle_policy" "alphapose_lifecycle_polcy" {
  repository = aws_ecr_repository.alphapose_repo.name

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


#ANIMATION API ECR REPO
resource "aws_ecr_repository" "animation_repo" {
  name                 = "animation_image_repo_qa"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    env = "model-testing"
  }

}

resource "aws_ecr_repository_policy" "animation-ecr-policy" {
  repository = aws_ecr_repository.animation_repo.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowPushPull",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : [
            "${aws_iam_role.devops_role.arn}",         #TASK EXECUTION IAM ROLE
            "${aws_iam_role.task_execution_role.arn}", #ML_DEVOPS IAM ROLE
            "${var.sketch_instance_arn}"
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

resource "aws_ecr_lifecycle_policy" "animation_lifecycle_polcy" {
  repository = aws_ecr_repository.animation_repo.name

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


#SKETCH API ECR REPO
resource "aws_ecr_repository" "sketch_repo" {
  name                 = "sketch_image_repo_qa"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    env = "model-testing"
  }

}

resource "aws_ecr_repository_policy" "sketch-ecr-policy" {
  repository = aws_ecr_repository.sketch_repo.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowPushPull",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : [
            "${aws_iam_role.devops_role.arn}",         #TASK EXECUTION IAM ROLE
            "${aws_iam_role.task_execution_role.arn}", #ML_DEVOPS IAM ROLE
            "${var.sketch_instance_arn}"
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

resource "aws_ecr_lifecycle_policy" "sketch_lifecycle_polcy" {
  repository = aws_ecr_repository.sketch_repo.name

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


resource null "build_images" {
   
   provisioner "local-exec" {
    command = "./build_detectron"
  }
}