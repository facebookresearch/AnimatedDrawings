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

  aliases = [var.video_alias]

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
    acm_certificate_arn = var.cloudfront_cert_arn
    ssl_support_method = "sni-only"
    #cloudfront_default_certificate = true
  }
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
  aliases = ["sketch${var.primary_hosted_zone}"]

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
    #cloudfront_default_certificate = true
    acm_certificate_arn = var.cloudfront_cert_arn
    ssl_support_method = "sni-only"
  }
}



resource "aws_route53_record" "www" {
  zone_id = var.hosted_zone_id
  name    = "sketch${var.primary_hosted_zone}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_cloudfront_distribution.www_distribution.domain_name]
}

resource "aws_route53_record" "video" {
  zone_id = var.hosted_zone_id
  name    = "prod-sketch-video${var.primary_hosted_zone}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_cloudfront_distribution.video_distribution.domain_name]
}

resource "aws_route53_record" "sketch_api" {
  zone_id = var.hosted_zone_id
  #name    = "sketch-api.${var.environment}${var.primary_hosted_zone}"
  name    = "${var.environment}-sketch-api${var.primary_hosted_zone}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.ecs_cluster_alb.dns_name]
}