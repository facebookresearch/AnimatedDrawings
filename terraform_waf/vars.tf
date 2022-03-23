variable "global_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "beta"
}
variable "PROFILE_ARN" {
  type = string
}

variable "waf_rules" {
  type    = list
  default = [
     {
      name = "AWSManagedRulesBotControlRuleSet"
      priority = 0
      managed_rule_group_statement_name = "AWSManagedRulesBotControlRuleSet"
      managed_rule_group_statement_vendor_name = "AWS"
      metric_name = "AWSManagedRulesBotControlRuleSet"
    },
    {
      name = "AWSManagedRulesKnownBadInputsRuleSet"
      priority = 1
      managed_rule_group_statement_name = "AWSManagedRulesKnownBadInputsRuleSet"
      managed_rule_group_statement_vendor_name = "AWS"
      metric_name = "AWSManagedRulesKnownBadInputsRuleSet"
    },
    {
      name = "AWSManagedRulesAmazonIpReputationList"
      priority = 2
      managed_rule_group_statement_name = "AWSManagedRulesAmazonIpReputationList"
      managed_rule_group_statement_vendor_name = "AWS"
      metric_name = "AWSManagedRulesAmazonIpReputationList"
    },
     {
      name = "AWSManagedRulesAnonymousIpList"
      priority = 3
      managed_rule_group_statement_name = "AWSManagedRulesAnonymousIpList"
      managed_rule_group_statement_vendor_name = "AWS"
      metric_name = "AWSManagedRulesAnonymousIpList"
    },
    {
      name = "AWSManagedRulesCommonRuleSet"
      priority = 4
      managed_rule_group_statement_name = "AWSManagedRulesCommonRuleSet"
      managed_rule_group_statement_vendor_name = "AWS"
      metric_name = "AWSManagedRulesCommonRuleSet"
    }
  ]
}
