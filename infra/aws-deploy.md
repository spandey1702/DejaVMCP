# AWS deployment notes

This project can be deployed as a containerized FastAPI service on AWS.

## Suggested services

- ECS Fargate or App Runner for the API
- Amazon S3 for artifact storage or decision snapshots
- IAM role with access to S3 and optionally Secrets Manager
- CockroachDB Cloud or a managed CockroachDB service for transactional task and decision storage

## Environment variables

- COCKROACH_DSN: connection string for CockroachDB
- AWS_REGION: target AWS region
- AWS_S3_BUCKET: bucket for storing ledger snapshots or exports

## Example deployment flow

1. Build the container image.
2. Push it to Amazon ECR.
3. Deploy it via ECS Fargate or App Runner.
4. Configure the environment variables above.
