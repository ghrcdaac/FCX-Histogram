#!/bin/bash

# Vars
account_id="307493436926"
region="us-east-1"
repository_name="histogram-preprocessing-v1"
#create new ECR repo
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account_id}.dkr.ecr.${region}.amazonaws.com
aws ecr create-repository --repository-name ${repository_name} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
# docker build image, tag it and push it to the ECR repo
docker build -t ${repository_name} .
docker tag  ${repository_name}:latest ${account_id}.dkr.ecr.${region}.amazonaws.com/${repository_name}:latest
docker push ${account_id}.dkr.ecr.${region}.amazonaws.com/${repository_name}:latest