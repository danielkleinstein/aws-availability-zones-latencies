resource "aws_dynamodb_table" "ec2_instance_metrics" {
  name         = "EC2InstanceMetrics"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "availability_zone_from"
  range_key    = "availability_zone_to"

  attribute {
    name = "availability_zone_from"
    type = "S"
  }

  attribute {
    name = "availability_zone_to"
    type = "S"
  }

  # TODO - change to us-east-1
  provider = aws.us_east_1
}

resource "aws_dynamodb_table" "ec2_instance_instructions" {
  name         = "EC2InstanceInstructions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "availability_zone"

  attribute {
    name = "availability_zone"
    type = "S"
  }

  # TODO - change to us-east-1
  provider = aws.us_east_1
}
