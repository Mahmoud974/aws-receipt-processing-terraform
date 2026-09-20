resource "random_id" "bucket_suffix" {
  byte_length = 3
}

resource "aws_s3_bucket" "receipts" {
  bucket = "${var.project_name}-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "receipts" {
  bucket = aws_s3_bucket.receipts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "receipts" {
  bucket = aws_s3_bucket.receipts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "receipts" {
  bucket = aws_s3_bucket.receipts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "receipts" {
  bucket = aws_s3_bucket.receipts.id

  rule {
    id     = "expire-old-receipts"
    status = "Enabled"

    filter {}

    expiration {
      days = var.receipt_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.receipt_retention_days
    }
  }
}

resource "aws_dynamodb_table" "receipts" {
  name         = "${var.project_name}-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "receipt_id"

  attribute {
    name = "receipt_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_ses_email_identity" "receipt_email" {
  email = var.ses_email
}
