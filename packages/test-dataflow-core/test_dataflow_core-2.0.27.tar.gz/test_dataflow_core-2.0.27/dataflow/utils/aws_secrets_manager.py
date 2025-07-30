import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError
import json
from utils.json_handler import JsonHandler

class SecretsManagerClient:
    """
    A class to interact with AWS Secrets Manager for managing secrets.

    Attributes:
        client: The Boto3 client for Secrets Manager.
        json_handler: An instance of JsonHandler for handling JSON operations.
    """
    def __init__(self):
        try:
            self.client = boto3.client('secretsmanager')
        except EndpointConnectionError as e:
            self.logger.error(f"Failed to initialize SecretsManagerClient: {e}")
            raise Exception(f"Failed to initialize SecretsManagerClient: Unable to connect to the endpoint. {e}")
        except NoCredentialsError as e:
            self.logger.error(f"Failed to initialize SecretsManagerClient: {e}")
            raise Exception(f"Failed to initialize SecretsManagerClient: No AWS credentials found. {e}")


    def get_secret_by_key(self, vault_path, user_name, secret_key: str):
        """
        Get information about a specific secret.

        Args:
            vault_path (str): The vault path.
            user_name (str): The user name.
            secret_key (str): The key of the secret to retrieve.

        Returns:
            str: Information about the secret in JSON format.

        Raises:
            Exception: If the operation fails.
        """
        try:
            if not user_name:
                raise Exception("user_name is required when secret_key is provided")

            secret_name = f"{user_name}/{vault_path}/{secret_key}"
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_metadata = self.client.describe_secret(SecretId=secret_name)
            secret_data = json.loads(response.get('SecretString'))

            if secret_data.get('is_active') == 'Y':
                secret_info={
                    "Name": secret_key,
                    "Description": secret_metadata.get('Description')
                }
                secret_info.update(secret_data)
                return secret_info
            else:
                raise Exception(f"Secret named '{secret_key}' is not active")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise Exception(f"Secret named '{secret_key}' not found")
            else:
                raise Exception(f"Failed to get secret '{secret_key}': {e}")
    
    def get_secret_value_by_key(self, vault_path: str, user_name: str, secret_key: str):
        """
        Get the 'value' field from the secret stored in AWS Secrets Manager.

        Args:
            vault_path (str): The path prefix (e.g., 'secrets').
            user_name (str): The user's name (can be empty if using runtime/slug).
            secret_key (str): The name of the secret key.

        Returns:
            str: The value of the secret (from 'value' field) or None if not found.
        """
        try:
            print("reached secret fucntion")
            secret_name = f"{vault_path}/{secret_key}"
            print(secret_name)
            response = self.client.get_secret_value(SecretId=secret_name)
            print("reached aws for secret value")
            secret_data = self.json_handler.json_to_dict(response.get('SecretString'))

            if secret_data.get("is_active") == "Y":
                print("active secret")
                return secret_data.get("value")
            else:
                print("not active")
                raise Exception(f"Secret named '{secret_key}' is not active")

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise Exception(f"Secret named '{secret_key}' not found")
            else:
                raise Exception(f"Failed to get secret '{secret_key}': {e}")