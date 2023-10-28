resource "aws_sqs_queue" "sqs_control_queue" {
  name = "sqs-control-queue"

  provider = aws.us_east_1
}
