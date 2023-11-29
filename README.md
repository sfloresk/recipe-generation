# Recipe generation 

This solution provides an example of how to create a end to end solution to inference images of food/dishes and create a recipe.

## Infrastructure

The infrastructure is based on:
1. Amazon API Gateway - Entry point to send images as base64 and recieve recipes
2. Amazon Lambda Function - Process the image invoking the BLIP2 and Claude instant models
3. Amazon Cognito - Authentication for the API
4. Amazon Sagemaker - Host BLIP2 model
5. Amazon Bedrock - send inference requests for Claude instant

Most of the deployment of the infrastructure is automated using the Serverless Application Model. For detail instructions, follows the steps [here](./infrastructure/README.md)

## Web portal

Example single page application built in Vue JS - it is integrated with Cognito to provide a seemlessly experience, allowing users to sign up and sign in. 

Detail instructions can be found [here](./web-portal/README.md)


