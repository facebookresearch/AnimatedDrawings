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
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  aliases = ["prod-sketch.metademolab.com"]

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
    acm_certificate_arn = var.cloudfront_cert_arn
    ssl_support_method = "sni-only"
  }
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
  aliases = ["prod-sketch-video.metademolab.com"]
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
    acm_certificate_arn = var.cloudfront_cert_arn
    ssl_support_method = "sni-only"
  }
}


resource "aws_route53_record" "www" {
  zone_id = var.public_hosted_zone_id
  name    = "${var.environment}-sketch${var.primary_dns_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_cloudfront_distribution.www_distribution.domain_name]
}

resource "aws_route53_record" "video" {
  zone_id = var.public_hosted_zone_id
  name    = "${var.environment}-sketch-video${var.primary_dns_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_cloudfront_distribution.video_distribution.domain_name]
}

# API ENDPOINTS IN PRIVATE HOSTED ZONE
resource "aws_route53_record" "private_api" {
  zone_id = var.private_hosted_zone_id
  name    = "${var.environment}-private-cluster-api${var.primary_dns_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.ecs_cluster_alb.dns_name]
}


# SKETCH API DOMAIN NAME 
resource "aws_route53_record" "sketch_public" {
  zone_id = var.public_hosted_zone_id
  name    = "${var.environment}-sketch-api${var.primary_dns_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.sketch_public_loadbalancer.dns_name]
}