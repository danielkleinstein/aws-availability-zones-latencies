resource "aws_sqs_queue" "sqs_control_queue" {
  name = "sqs-control-queue"

  provider = aws.ap_south_2
}
