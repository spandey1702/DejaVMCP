import os
from typing import Optional


class Settings:
    cockroach_dsn: Optional[str] = os.getenv("COCKROACH_DSN")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_s3_bucket: Optional[str] = os.getenv("AWS_S3_BUCKET")


settings = Settings()
