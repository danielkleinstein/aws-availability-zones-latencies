output "ec2_instance_metrics_table_name" {
  value = aws_dynamodb_table.ec2_instance_metrics.name
}

output "ec2_instance_instructions_table_name" {
  value = aws_dynamodb_table.ec2_instance_instructions.name
}
