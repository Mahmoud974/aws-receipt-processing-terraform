variable "aws_region" {
  description = "AWS region used by the project. Keep all services in the same region."
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Prefix used for AWS resource names."
  type        = string
  default     = "receipt-processing-md-august"
}

variable "ses_email" {
  description = "Email address used as SES sender and recipient. In SES sandbox this address must be verified."
  type        = string
}

variable "lambda_memory_size" {
  description = "Memory allocated to the Lambda function in MB."
  type        = number
  default     = 128
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "Number of days to keep the Lambda CloudWatch logs."
  type        = number
  default     = 30
}

variable "receipt_retention_days" {
  description = "Number of days to keep receipt files in S3 before they expire."
  type        = number
  default     = 365
}
