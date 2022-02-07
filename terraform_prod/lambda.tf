provider "archive" {}

data "archive_file" "consent_uploads" {
  type        = "zip"
  source_file = "consent_uploads.py"
  output_path = "consent_uploads.zip"
}

data "archive_file" "query_s3" {
  type        = "zip"
  source_file = "query_s3.py"
  output_path = "query_s3.zip"
}

data "aws_iam_policy_document" "policy" {
  statement {
    sid    = ""
    effect = "Allow"

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "lambda_iam_${var.environment}"
  assume_role_policy = "${data.aws_iam_policy_document.policy.json}"
}

resource "aws_iam_policy_attachment" "lambda_iam_policy_attach" {
  name  = "lambda-function-policy-attachment-${var.environment}"
  roles = [aws_iam_role.iam_for_lambda.name]

  for_each = toset([
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/CloudfrontFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchLogsReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
  ])

  policy_arn = each.value

}


resource "aws_lambda_function" "consents_upload_lambda" {
  function_name = "consent_uploads_${var.environment}"
  timeout = 900

  filename         = "${data.archive_file.consent_uploads.output_path}"
  source_code_hash = "${data.archive_file.consent_uploads.output_base64sha256}"

  role    = "${aws_iam_role.iam_for_lambda.arn}"
  handler = "consent_uploads.lambda_handler"
  runtime = "python3.6"

  environment {
    variables = {
      greeting = "Hello"
    }
  }
}

resource "aws_lambda_function" "query_s3_lambda" {
  function_name = "query_s3_${var.environment}"
  timeout = 900

  filename         = "${data.archive_file.query_s3.output_path}"
  source_code_hash = "${data.archive_file.query_s3.output_base64sha256}"

  role    = "${aws_iam_role.iam_for_lambda.arn}"
  handler = "query_s3.lambda_handler"
  runtime = "python3.6"

  environment {
    variables = {
      consents_upload_function_arn = "${aws_lambda_function.consents_upload_lambda.arn}",
      page_count = 15
    }
  }
}

resource "aws_cloudwatch_event_rule" "querys3_lambda_cron" {
    name = "querys3lambda-scheduler-${var.environment}"
    description = "querys3upload lambda scheduler"
    schedule_expression = "cron(0/5 * * * ? *)" 
}

resource "aws_cloudwatch_event_target" "consents_lambda_target" {
    rule = "${aws_cloudwatch_event_rule.querys3_lambda_cron.name}"
    target_id = "querys3_lambda_target_${var.environment}"
    arn = "${aws_lambda_function.query_s3_lambda.arn}"
}

resource "aws_lambda_permission" "query_lambda_permission" {
    statement_id = "AllowExecutionFromCloudWatch-${var.environment}"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.query_s3_lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.querys3_lambda_cron.arn}"
}