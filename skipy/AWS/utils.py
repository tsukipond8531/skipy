import boto3


class ParameterStore:
    def __init__(self, region="ap-northeast-1"):
        self.region = region

    def get(self, key):
        try:
            ssm = boto3.client(
                "ssm",
                region_name=self.region,
                endpoint_url=f"https://ssm.{self.region}.amazonaws.com",
            )
            response = ssm.get_parameters(
                Names=[
                    key,
                ],
                WithDecryption=True,
            )
        except Exception as e:
            raise e
        return response["Parameters"][0]["Value"]
