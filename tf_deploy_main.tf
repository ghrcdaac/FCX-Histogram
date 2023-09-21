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

  environment {
    variables = {
      BUCKET_AWS_REGION = var.aws_region
      SOURCE_BUCKET_NAME = var.SOURCE_BUCKET_NAME
    }
  }
}

## 2.3. CREATE CLOUDWATCH LOG GROUP ##

# log lambda
resource "aws_cloudwatch_log_group" "histogram_tool_preprocessing" {
  name = "/aws/lambda/${aws_lambda_function.histogram_tool_preprocessing.function_name}"

  retention_in_days = 5
}



## 3. Configure REST API gateway for the lambda.

## REST API GATEWAY

# API Gateway name
resource "aws_api_gateway_rest_api" "histogram_tool_preprocessing" {
  name = "fcx-histogram-preprocessing-api"
}


## create resource
resource "aws_api_gateway_resource" "histogram_tool_preprocessing" {
  path_part   = aws_lambda_function.histogram_tool_preprocessing.function_name
  parent_id   = aws_api_gateway_rest_api.histogram_tool_preprocessing.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
}

## create method
resource "aws_api_gateway_method" "histogram_tool_preprocessing" {
  rest_api_id   = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
  resource_id   = aws_api_gateway_resource.histogram_tool_preprocessing.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true
}

## allow CORS on preflight
module "subset_trigger_api_cors" {
  source = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
  api_resource_id = aws_api_gateway_resource.histogram_tool_preprocessing.id

  depends_on = [ aws_api_gateway_rest_api.histogram_tool_preprocessing, aws_api_gateway_resource.histogram_tool_preprocessing ]
}


## INTEGRATION OF GATEWAY AND LAMBDA TRIGGER
resource "aws_api_gateway_integration" "histogram_tool_preprocessing" {
  rest_api_id             = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
  resource_id             = aws_api_gateway_resource.histogram_tool_preprocessing.id
  http_method             = aws_api_gateway_method.histogram_tool_preprocessing.http_method
  integration_http_method = aws_api_gateway_method.histogram_tool_preprocessing.http_method
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.histogram_tool_preprocessing.invoke_arn
}


## PERMISSIONS to trigger lamba from api gateway
resource "aws_lambda_permission" "histogram_tool_preprocessing" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.histogram_tool_preprocessing.function_name
  principal     = "apigateway.amazonaws.com"
  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.aws_region}:${var.accountId}:${aws_api_gateway_rest_api.histogram_tool_preprocessing.id}/*/${aws_api_gateway_method.histogram_tool_preprocessing.http_method}${aws_api_gateway_resource.histogram_tool_preprocessing.path}"
}


## SET RESPONSE HANDLERS FOR API-GATEWAY (NOT NEEDED FOR AWS PROXY INTEGRATION) HANDLE CORS HEADERS FROM LAMBDA RESPONSE ITSELF


## Create deployment for histogram_tool_preprocessing
resource "aws_api_gateway_deployment" "histogram_tool_preprocessing" {
  rest_api_id = aws_api_gateway_rest_api.histogram_tool_preprocessing.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.histogram_tool_preprocessing.id,
      aws_api_gateway_method.histogram_tool_preprocessing.id,
      aws_api_gateway_integration.histogram_tool_preprocessing.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

## create stage for the histogram_tool_preprocessing
resource "aws_api_gateway_stage" "histogram_tool_preprocessing" {
  deployment_id = aws_api_gateway_deployment.histogram_tool_preprocessing.id
  rest_api_id   = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
  stage_name    = var.stage_name
  depends_on = [aws_cloudwatch_log_group.histogram_tool_preprocessing_api]
}



### to enable api key and its usage plan for histogram_tool_preprocessing

# create api key
resource "aws_api_gateway_api_key" "histogram_tool_preprocessing_api_key" {
  name = "histogram_preprocessing_api-key"
}

# create usage plans
resource "aws_api_gateway_usage_plan" "histogram_tool_preprocessing_api_usagePlan" {
  name         = "histogram_preprocessing_api-usagePlan"
  description  = "Usage plan for the histogram_preprocessing_api key"

  api_stages {
    api_id = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
    stage  = aws_api_gateway_stage.histogram_tool_preprocessing.stage_name
  }
}

resource "aws_api_gateway_usage_plan_key" "histogram_usagePlan_with_key" {
  key_id        = aws_api_gateway_api_key.histogram_tool_preprocessing_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.histogram_tool_preprocessing_api_usagePlan.id
}


## add and enable cloudwatch logs for subset_trigger_api

resource "aws_cloudwatch_log_group" "histogram_tool_preprocessing_api" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.histogram_tool_preprocessing.id}/${var.stage_name}"
  retention_in_days = 3
}

resource "aws_api_gateway_method_settings" "histogram_tool_preprocessing_api_method" {
  rest_api_id = aws_api_gateway_rest_api.histogram_tool_preprocessing.id
  stage_name  = aws_api_gateway_stage.histogram_tool_preprocessing.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

## Add role to allow API Gateway to write logs

# create role
resource "aws_iam_role" "cloudwatch" {
  name = "api_gateway_cloudwatch_global"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

# create policy
data "aws_iam_policy_document" "cloudwatch" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents",
    ]

    resources = ["*"]
  }
}

# add policy to role
resource "aws_iam_role_policy" "cloudwatch" {
  name   = "cloudwatch_logs_default_policy"
  role   = aws_iam_role.cloudwatch.id
  policy = data.aws_iam_policy_document.cloudwatch.json
}

# Add role in API Gateway Account Settigns
resource "aws_api_gateway_account" "apigateway_cloudwatch_role" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch.arn
}