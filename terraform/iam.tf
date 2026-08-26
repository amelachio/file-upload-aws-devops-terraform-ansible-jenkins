resource "aws_iam_role" "backend_role" {
  name = "3tier-backend-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "3tier-backend-role"
  }
}

resource "aws_iam_role_policy" "backend_s3_access" {
  name = "3tier-backend-s3-policy"
  role = aws_iam_role.backend_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.file_upload.arn}/*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "backend_profile" {
  name = "3tier-backend-instance-profile"
  role = aws_iam_role.backend_role.name
}
