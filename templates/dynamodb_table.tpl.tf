resource "aws_dynamodb_table" "ec2_instance_metrics" {
  name         = "EC2InstanceMetrics"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "availability_zone"

  attribute {
    name = "availability_zone"
    type = "S"
  }

  # TODO - change to us-east-1
  provider = aws.ap_south_2
}
