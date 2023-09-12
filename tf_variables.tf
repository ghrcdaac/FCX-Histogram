## variables for aws provider
variable "aws_creds_path" {
  description = "The path to aws credentials file"

  type    = string
  default = "~/.aws/credentials"
}

variable "aws_region" {
  description = "AWS region for all resources."

  type    = string
}

## variables for worker lambdas code

variable "SOURCE_BUCKET_NAME" {
  description = "Bucket with raw data files required for the subset-worker"

  type    = string
  default = "fcx-raw-data-temp"
}

## variables needed for ECR image url

variable "ecr_name" {
  type    = string
  default = "fcx-histogram-preprocessing"
}

variable "accountId" {
  type    = string
}


## variables for worker lambda configuration

variable "lambda_execution_timeout" {
  description = "lambda execution time limit in seconds"

  type    = number
  default = 603
}

variable "lambda_execution_memory" {
  description = "Maximum memory that the lambda execution can use (in MB). Processing power is directly proportional to the memory size"

  type    = number
  default = 1024
}

variable "lambda_execution_ephimeral_storage" {
  description = "Maximum storage of /tmp that the lambda execution can use (in MB)."

  type    = number
  default = 5120
}


## variables needed for API GATEWAYS


variable "stage_name" {
  type    = string
  default = "development"
}

