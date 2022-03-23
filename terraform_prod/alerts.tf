locals {
  emails = ["christopher897@fb.com", "somyaj@fb.com"]
}


resource "aws_cloudwatch_metric_alarm" "ecs-alert_High-MemReservation" {
  alarm_name = "sketch-animation-${var.environment}-ECS-High_MemResv"
  comparison_operator = "GreaterThanOrEqualToThreshold"

  period = "60"
  evaluation_periods = "1"
  datapoints_to_alarm = 1

  statistic = "Average"
  threshold = "80"
  alarm_description = ""

  metric_name = "MemoryReservation"
  namespace = "AWS/ECS"
  dimensions = {
    ClusterName = "${aws_ecs_cluster.ecs_cluster.name}"
  }

  actions_enabled = true
  insufficient_data_actions = []
  ok_actions = []
  alarm_actions = [
    "${aws_sns_topic.sketch_animation.arn}",
  ]
}


resource "aws_sns_topic" "sketch_animation" {
  name = "sketch-animation-alerts-topic"
}

resource "aws_sns_topic_subscription" "sketch_animation" {
  count     = length(local.emails)
  topic_arn = aws_sns_topic.sketch_animation.arn
  protocol  = "email"
  endpoint  = local.emails[count.index]
}