import base64
import json
import boto3
import os
import logging
import sys
   
# Setup logging
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(stdout_handler)


# Get enviroment
endpoint_name = os.getenv("BLIP2_SM_ENDPOINT_NAME")

## Init clients
bedrock = boto3.client("bedrock-runtime", 'us-east-1')
smr_client = boto3.client("sagemaker-runtime")

def run_inference(endpoint_name, inputs):
    response = smr_client.invoke_endpoint(
        EndpointName=endpoint_name, Body=json.dumps(inputs)
    )
    return response["Body"].read().decode('utf-8')

def lambda_handler(event, context):
    logger.info(event)
    request_json = json.loads(event['body'])
    if "image_b64" not in request_json.keys():
        return {'statusCode':400}
    # Getting the image description
    inputs = {"image": request_json['image_b64']}
    image_description_result = run_inference(endpoint_name, inputs)
    # Now asking for ingredients
    inputs = {"prompt": "Question: What ingredients are in this foto? Answer:", "image": request_json['image_b64']}
    image_ingredients_result = run_inference(endpoint_name, inputs)
    # Checking if are any constraints in the request
    if "constraints" in request_json.keys():
        # Asking claude for a recipe and ingredients with the constraints
        prompt_message = f'''Human: You are a chef that create recipes from a dish description and ingredients
        <image_description>
        {image_description_result}
        </image_description>
        <ingredients>
        {image_ingredients_result}
        </ingredients>
        Create a step by step recipe including the ingredients with the following constraints {request_json['constraints']}. If you don't know the answer, say "I don't know"
        
        Assistant:
        '''
    else:
        # Asking claude for a recipe and ingredients with no constraints
        prompt_message = f'''Human: You are a chef that create recipes from a dish description and ingredients
        <image_description>
        {image_description_result}
        </image_description>
        <ingredients>
        {image_ingredients_result}
        </ingredients>
        Create a step by step recipe including the ingredients. If you don't know the answer, say "I don't know"
        
        Assistant:
        '''
    claude_request_body={'prompt': prompt_message, 'max_tokens_to_sample': 2048, 'temperature': 0, 'top_k': 250, 'top_p': 0.999, 'stop_sequences': ['\n\nHuman:'], 'anthropic_version': 'bedrock-2023-05-31'}
    logger.info(f"Sending message: {prompt_message}")
    response = bedrock.invoke_model(
        body=json.dumps(claude_request_body), 
        modelId='anthropic.claude-instant-v1', 
        accept='*/*',
        contentType="application/json")
    logger.info(f"Model replied - parsing result")
    response_body = json.loads(response.get('body').read())
    logger.info(f"message: {response_body['completion']}")
    recipe_generation = response_body['completion']
    lambda_response_body = json.dumps({
        'recipe_generation':recipe_generation,
        'dish_name': image_description_result
    })
    return {
        'statusCode':200,
        "isBase64Encoded":False,
        "headers": {"content-type":"application/json", "access-control-allow-origin":"*"},
        "body":f"{lambda_response_body}"
        }
    