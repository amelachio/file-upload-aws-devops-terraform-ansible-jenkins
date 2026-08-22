resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "file_upload" {
  bucket = "file-upload-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "3tier-file-upload-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "file_upload" {
  bucket = aws_s3_bucket.file_upload.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
