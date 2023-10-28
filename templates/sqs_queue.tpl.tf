
resource "aws_sqs_queue" "sqs_queue_REGION_AZ_REPLACE_ME" {
  name = "sqs-queue-experiment_REGION_AZ_REPLACE_ME"

  provider = aws.REGION_ALIAS_REPLACE_ME
}
