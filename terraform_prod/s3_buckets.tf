# NONCONSENTS BUCKET
resource "aws_s3_bucket" "non_consent" {

  bucket = var.non_consent_bucket
  acl    = "private"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["*"]
        }
        "Action" : ["s3:*"],
        "Resource" : ["arn:aws:s3:::${var.non_consent_bucket}/*"]
      }
    ],
  })

}

# NONCONSENTS BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "non_consentblock" {
  bucket = aws_s3_bucket.non_consent.id

  block_public_acls       = true
  #block_public_policy     = true
  #ignore_public_acls      = true
  #restrict_public_buckets = true
}


# WWW BUCKET
resource "aws_s3_bucket" "www" {

  bucket = var.www_domain_name
  acl    = "private"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["${aws_cloudfront_origin_access_identity.www_OAI.iam_arn}"]
        }
        "Action" : ["s3:GetObject"],
        "Resource" : ["arn:aws:s3:::${var.www_domain_name}/*"]
      }
    ],
  })

  website {
    #sredirect_all_requests_to = "https://${var.www_domain_name}"
    index_document = "index.html"
    error_document = "index.html"
  }
}

# WWW BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "www_block" {
  bucket = aws_s3_bucket.www.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}




# VIDEO BUCKET
resource "aws_s3_bucket" "video" {

  bucket = var.video_bucket
  acl    = "private"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["${aws_cloudfront_origin_access_identity.video_OAI.iam_arn}"]
        }
        "Action" : ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
        "Resource" : ["arn:aws:s3:::${var.video_bucket}/*"]
      }
    ],
  })
}




#VIDEO BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "video_block" {
  bucket = aws_s3_bucket.video.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# INTERIM BUCKET
resource "aws_s3_bucket" "interim" {

  bucket = var.interim_bucket
  acl    = "private"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["*"]
        }
        "Action" : ["s3:*"],
        "Resource" : ["arn:aws:s3:::${var.interim_bucket}", "arn:aws:s3:::${var.interim_bucket}/*"]
      }
    ],
  })

}

# INTERIM BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "interim_block" {
  bucket = aws_s3_bucket.interim.id

  #block_public_acls       = true
  #block_public_policy     = true
  #ignore_public_acls      = true
  #restrict_public_buckets = true
}



# CONSENTS BUCKET 
resource "aws_s3_bucket" "consents" {

  bucket = var.consents_bucket
  acl    = "private"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["*"]
        }
        "Action" : ["s3:GetObject"],
        "Resource" : ["arn:aws:s3:::${var.consents_bucket}/*"]
      }
    ],
  })

}

# CONSENTS BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "consents_block" {
  bucket = aws_s3_bucket.consents.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}


data "aws_canonical_user_id" "current" {}

resource "aws_s3_bucket" "logs" {

  bucket = var.logs_bucket
  #acl    = "private"

  grant {
    id          = data.aws_canonical_user_id.current.id
    permissions = ["FULL_CONTROL"]
    type        = "CanonicalUser"
  }

  grant {
    id          = "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0" #AWS CLOUDFRONT DEFAULT CANONICAL ID
    permissions = ["FULL_CONTROL"]
    type        = "CanonicalUser"
  }

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "AddPerm",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : ["*"]
        }
        "Action" : ["s3:GetObject", "s3:PutObject"],
        "Resource" : ["arn:aws:s3:::${var.logs_bucket}/*"]
      },
    ],
  })
}

# LOGS BUCKET BLOCK
resource "aws_s3_bucket_public_access_block" "logs_block" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}