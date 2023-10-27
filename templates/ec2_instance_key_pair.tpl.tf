resource "tls_private_key" "development_server_private_key_REGION_ALIAS_REPLACE_ME" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "private_key_file_REGION_ALIAS_REPLACE_ME" {
  content  = tls_private_key.development_server_private_key_REGION_ALIAS_REPLACE_ME.private_key_pem
  filename = "development_server_key_REGION_ALIAS_REPLACE_ME.pem"
}

resource "local_file" "public_key_file_REGION_ALIAS_REPLACE_ME" {
  content  = tls_private_key.development_server_private_key_REGION_ALIAS_REPLACE_ME.public_key_openssh
  filename = "development_server_key_pub_REGION_ALIAS_REPLACE_ME.pem"
}

resource "aws_key_pair" "development_server_key_pair_REGION_ALIAS_REPLACE_ME" {
  key_name   = "development-server-key-pair-REGION_NAME_REPLACE_ME"
  public_key = tls_private_key.development_server_private_key_REGION_ALIAS_REPLACE_ME.public_key_openssh

  provider = aws.REGION_ALIAS_REPLACE_ME
}

