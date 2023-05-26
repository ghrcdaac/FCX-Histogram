#!/bin/bash

# Vars
# Get using env variables
TF_VAR_ecr_name="fcx-histogram-preprocessing"

#create new ECR repo
aws ecr get-login-password --region ${TF_VAR_aws_region} | docker login --username AWS --password-stdin ${TF_VAR_accountId}.dkr.ecr.${TF_VAR_aws_region}.amazonaws.com
export AWS_PAGER=""
aws ecr create-repository --repository-name ${TF_VAR_ecr_name} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

# docker build image, tag it and push it to the ECR repo
docker build -t ${TF_VAR_ecr_name} .
docker tag  ${TF_VAR_ecr_name}:latest ${TF_VAR_accountId}.dkr.ecr.${TF_VAR_aws_region}.amazonaws.com/${TF_VAR_ecr_name}:latest
docker push ${TF_VAR_accountId}.dkr.ecr.${TF_VAR_aws_region}.amazonaws.com/${TF_VAR_ecr_name}:latest

# vars needed for terraform:
echo "ECR DOCKER IMAGE URL:"
echo ${TF_VAR_accountId}.dkr.ecr.${TF_VAR_aws_region}.amazonaws.com/${TF_VAR_ecr_name}:latest