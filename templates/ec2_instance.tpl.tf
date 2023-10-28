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

  user_data = <<-EOF
              #!/bin/bash
              echo "${aws_sqs_queue.sqs_queue_REGION_ALIAS_REPLACE_ME.url}" > /sqs-queue
              sudo apt update -y
              sudo apt install iperf3 -y
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