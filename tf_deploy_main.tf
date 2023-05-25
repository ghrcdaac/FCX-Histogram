########## COMMON DECLARATIONS ##########

## CONFIGURE AWS PROVIDER ##
provider "aws" {
  shared_credentials_files = [var.aws_creds_path]
  region = var.aws_region
}



## 1 Deploy the script to ECR using the deploy script. The deploy script takes in account_id, region and repository_name as variables, so set them accordingly.

# 1.1 In the AWS ECR, create a repository with repository_name
# 1.2 Upload the docker image to the ECR.
# Run `predeploy` bash script



## 2. Create a new lambda function (using docker), and select the deployed repository_name

# 2.1 Create ROLE
resource "aws_iam_role" "histogram_tool_preprocessing_role" {
  name = "fcx-histogram_tool_preprocessing_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


# policy defination
data "aws_iam_policy_document" "histogram_tool_aws_access" {
  statement {
    effect = "Allow"
    actions = ["s3:GetObject", "s3-object-lambda:*"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "histogram_tool_aws_access" {
  name        = "fcx_histogram_tool_aws_access"
  path        = "/"
  description = "IAM policy that allows a lambda to get s3 object"
  policy      = data.aws_iam_policy_document.histogram_tool_aws_access.json
}


# attach policies to role
resource "aws_iam_role_policy_attachment" "lambda_policy_basic" {
  role       = aws_iam_role.histogram_tool_preprocessing_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "histogram_tool_aws_access" {
  role       = aws_iam_role.histogram_tool_preprocessing_role.name
  policy_arn = aws_iam_policy.histogram_tool_aws_access.arn
}


# 2.2 Create lambda function
resource "aws_lambda_function" "histogram_tool_preprocessing" {
  package_type = "Image"
  function_name = "fcx-histogram-preprocessing"
  image_uri = "${var.accountId}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_name}:latest"
  role = aws_iam_role.histogram_tool_preprocessing_role.arn

  memory_size = var.lambda_execution_memory
  timeout = var.lambda_execution_timeout

  ephemeral_storage {
    size = var.lambda_execution_ephimeral_storage
  }
}



## 3. Configure REST API gateway for the lambda.


# In the API gateway console, Allow CORS for resource, and re-deploy the API gateway.