# WWW BUCKET and CDN 
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

resource "aws_s3_bucket_public_access_block" "www_block" {
  bucket = aws_s3_bucket.www.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_identity" "www_OAI" {
}

resource "aws_cloudfront_distribution" "www_distribution" {

  origin {

    domain_name = aws_s3_bucket.www.bucket_regional_domain_name
    origin_id   = var.www_domain_name
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.www_OAI.cloudfront_access_identity_path
    }
  }

  custom_error_response {
    error_code    = 403
    response_code = 200
    response_page_path = "/index.html"
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    // This needs to match the `origin_id` above.
    target_origin_id = var.www_domain_name
    min_ttl          = 0
    default_ttl      = 86400
    max_ttl          = 31536000

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  // Here we're ensuring we can hit this distribution using www.runatlantis.io
  // rather than the domain name CloudFront gives us.
  // aliases = ["${var.www_domain_name}"]

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
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

# VIDEO OAI
resource "aws_cloudfront_origin_access_identity" "video_OAI" {
}

# VIDEO CDN
resource "aws_cloudfront_distribution" "video_distribution" {
  origin {

    domain_name = aws_s3_bucket.video.bucket_regional_domain_name
    origin_id   = aws_s3_bucket.video.bucket_domain_name
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.video_OAI.cloudfront_access_identity_path
    }
  }

  enabled = true

  // All values are defaults from the AWS console.
  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    // This needs to match the `origin_id` above.
    target_origin_id = aws_s3_bucket.video.bucket_domain_name
    min_ttl          = 0
    default_ttl      = 86400
    max_ttl          = 31536000

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

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
        "Action" : ["s3:GetObject"],
        "Resource" : ["arn:aws:s3:::${var.interim_bucket}/*"]
      }
    ],
  })

}

resource "aws_s3_bucket_public_access_block" "interim_block" {
  bucket = aws_s3_bucket.interim.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}

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

resource "aws_s3_bucket_public_access_block" "consents_block" {
  bucket = aws_s3_bucket.interim.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
}