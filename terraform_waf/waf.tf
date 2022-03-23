resource "aws_wafv2_web_acl" "beta_waf" {
  name        = "sketch_animation_waf"
  description = "Example of a managed rule."
  scope       = "CLOUDFRONT"

  default_action {
    block {}
  }

  dynamic "rule" {
  for_each = toset(var.waf_rules)

  content {
    name = rule.value.name
    priority = rule.value.priority
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name = rule.value.managed_rule_group_statement_name
        vendor_name = rule.value.managed_rule_group_statement_vendor_name
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = rule.value.metric_name
      sampled_requests_enabled   = true
    }
  }
}

  tags = {
    Tag1 = "waf_acl"
    Tag2 = "Terraform Managed"
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-acl"
    sampled_requests_enabled   = true
  }
}


resource "aws_cloudwatch_log_group" "waf_log_group" {
  name = "aws-waf-logs-sketch-animation"

  tags = {
    Environment = "beta"
    Application = "sketch_animation"
  }
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_logging" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.beta_waf.arn
}

#resource "aws_wafv2_web_acl_association" "acl-association" {
#  resource_arn = aws_cloudwatch_log_group.waf_log_group.arn
#  web_acl_arn = aws_wafv2_web_acl.beta_waf.arn
#}