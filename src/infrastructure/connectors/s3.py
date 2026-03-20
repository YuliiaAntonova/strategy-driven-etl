class S3Connector:
    def __init__(self, client=None, bucket_name: str | None = None):
        self.client = client
        self.bucket_name = bucket_name

    def connect(self):
        if self.client is None:
            raise NotImplementedError("Передай boto3 client при реальном использовании")
        return self.client
