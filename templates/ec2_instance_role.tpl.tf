resource "aws_iam_role" "ec2_instance_iam_role" {
  name = "ec2-instance-iam-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ec2_instance_iam_policy" {
  name = "ec2-instance-iam-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:*",
          "sqs:*",
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ec2_instance_policy" {
  role       = aws_iam_role.ec2_instance_iam_role.name
  policy_arn = aws_iam_policy.ec2_instance_iam_policy.arn
}

resource "aws_iam_instance_profile" "ec2_instance_iam_profile" {
  role = aws_iam_role.ec2_instance_iam_role.name
}
