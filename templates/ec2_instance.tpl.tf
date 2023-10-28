resource "aws_instance" "ec2_instance_REGION_AZ_REPLACE_ME" {
  provider          = aws.REGION_ALIAS_REPLACE_ME
  instance_type     = "t3.micro"
  ami               = "REGION_AMI_REPLACE_ME"
  availability_zone = "REGION_AZ_REPLACE_ME"
  key_name          = aws_key_pair.development_server_key_pair_REGION_ALIAS_REPLACE_ME.key_name
  vpc_security_group_ids = [
    aws_security_group.allow_ssh_security_group_REGION_ALIAS_REPLACE_ME.id,
    aws_security_group.allow_all_outbound_traffic_security_group_REGION_ALIAS_REPLACE_ME.id,
    aws_security_group.allow_iperf3_traffic_REGION_ALIAS_REPLACE_ME.id,
    aws_security_group.allow_ping_traffic_REGION_ALIAS_REPLACE_ME.id
  ]
  iam_instance_profile = aws_iam_instance_profile.ec2_instance_iam_profile.name

  user_data = <<-EOF
              #!/bin/bash
              echo "${aws_sqs_queue.sqs_queue_REGION_AZ_REPLACE_ME.url}" > /sqs-queue
              echo "${aws_dynamodb_table.ec2_instance_metrics.name}" > /dynamodb-write-table
              echo "${aws_dynamodb_table.ec2_instance_instructions.name}" > /dynamodb-read-table
              echo "REGION_NAME_REPLACE_ME" > /region
              echo "REGION_AZ_REPLACE_ME" > /az

              chmod 777 /sqs-queue /dynamodb-table /region
              apt update -y
              apt install iperf3 python3-pip -y

              iperf3 -s &

              mkdir /user-data-output
              chmod 777 /user-data-output

              su - ubuntu -c "pip3 install boto3"
              su - ubuntu -c "git clone https://github.com/danielkleinstein/aws-availability-zones-latencies.git repo"
              su - ubuntu -c "cd repo && python3 user-data.py > log.txt 2>&1"
              EOF

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 16
    delete_on_termination = true
    tags = {
      Name = "Instance_REGION_AZ_REPLACE_ME-volume"
    }
  }

  tags = {
    Name = "Instance_REGION_AZ_REPLACE_ME"
  }
}
