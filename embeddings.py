from dotenv import load_dotenv
load_dotenv()
import json
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def embed(text: str) -> list[float]:
    body = json.dumps({
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": "GENERIC_INDEX",
            "embeddingDimension": 1024,
            "text": {
                "truncationMode": "END",
                "value": text
            }
        }
    })
    response = client.invoke_model(
        modelId="amazon.nova-2-multimodal-embeddings-v1:0",
        body=body,
    )
    raw = json.loads(response["body"].read())
    return raw["embeddings"][0]["embedding"]

if __name__ == "__main__":
    embed("add authentication to the payments endpoint")
