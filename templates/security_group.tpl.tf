resource "aws_security_group" "allow_ssh_security_group_REGION_ALIAS_REPLACE_ME" {
  name        = "allow-ssh_REGION_ALIAS_REPLACE_ME"
  description = "Allow SSH inbound traffic for REGION_ALIAS_REPLACE_ME"
  provider    = aws.REGION_ALIAS_REPLACE_ME

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_iperf3_traffic_REGION_ALIAS_REPLACE_ME" {
  name        = "allow_iperf3_traffic_REGION_ALIAS_REPLACE_ME"
  description = "Allow iperf3 inbound traffic for REGION_ALIAS_REPLACE_ME"
  provider    = aws.REGION_ALIAS_REPLACE_ME

  ingress {
    from_port   = 5201
    to_port     = 5201
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_ping_traffic_REGION_ALIAS_REPLACE_ME" {
  name        = "allow_ping_traffic_REGION_ALIAS_REPLACE_ME"
  description = "Allow ping inbound traffic for REGION_ALIAS_REPLACE_ME"
  provider    = aws.REGION_ALIAS_REPLACE_ME

  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "allow_all_outbound_traffic_security_group_REGION_ALIAS_REPLACE_ME" {
  name        = "allow-all-outbound-traffic_REGION_ALIAS_REPLACE_ME"
  description = "Allow all outbound traffic for REGION_ALIAS_REPLACE_ME"
  provider    = aws.REGION_ALIAS_REPLACE_ME

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 means all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }
}
