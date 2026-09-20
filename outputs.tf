output "s3_bucket_name" {
  description = "Upload receipt images/PDFs to this bucket."
  value       = aws_s3_bucket.receipts.bucket
}

output "dynamodb_table_name" {
  description = "DynamoDB table containing extracted receipt data."
  value       = aws_dynamodb_table.receipts.name
}

output "lambda_function_name" {
  description = "Lambda function processing uploaded receipts."
  value       = aws_lambda_function.receipt_processor.function_name
}

output "ses_identity" {
  description = "SES email identity used by the project."
  value       = aws_ses_email_identity.receipt_email.email
}
