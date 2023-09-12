# Steps to deploy the histogram preprocessing script in the AWS lambda

It is supposed that the user has some prior knowledge about lambda and docker.

## Pre-requisites

- [(Install and) Configure Docker](https://docs.docker.com/engine/install/)
- [Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
- [Setup AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
  - `aws configure` Preferred. This deployment will assume that aws configure is used.
  - Need ```aws_access_key_id and aws_secret_access_key``` key values; inside `~/.aws/credentials`

## Deployement Details

1. Export env variables for keys mentioned in .env.example into shell session.
     - example: `export TF_VAR_aws_region="xxxxxxx" TF_VAR_accountId="xxxxxxx"`
     - These are optional (has a default value. ref. *_varaiables_*.tf files) `export TF_VAR_SOURCE_BUCKET_NAME=*********`
     - For more tweaking, ref. `.env.example`
2. Deploy using `bash deploy.sh`. The bash script does the following things:
     1. Deploy the script to ECR using the predeploy script.
       - `bash predeploy.sh`
            - This will create a repository in the AWS ECR and
            -  Build and upload the docker image to the ECR.
     2. Uses the following terraform commands to build and deploy the infrastrucutre needed   for Histogram Preprocessing Tool:
          - `terraform init`
          - `terraform plan`
          - `terraform apply`
               - This will create a new lambda function (using docker inn ECR)
               - Configure REST API gateway for the lambda.
               - Add appropriate roles and permissions.
               - Add cloudwatch logs for the API and Lambda.
               - And add necessary configuration for the lambda execution environment.
3. Use the `Histogram_preprocessed_data.postman_collection.json` postman collection to test the Lambda.

After terraform finishes building the Histogram tool infrastructure, it outputs env varaibles that can be used in the frontend.

- For `<sensitive>` as output value, use `terraform output <key_name>`

### To remove the Histogram preprocessing Tool

1. Run `terraform destroy`
     - removes the Lambda function, API Gateway and permissions.
2. Goto AWS ECR Management console and remove the created ECR.
