"""Utility functions and classes for configuration loading and dataset access."""

from dataclasses import dataclass

import requests
import yaml


@dataclass
class ConfigLoader:
    """A class to load configuration from a YAML file."""
    
    config_file: str = "./src/configs/datasets.yaml"
    # config_file: str = "./configs/datasets.yaml"

    def __post_init__(self):
        """Post-initialization checks for the config file."""
        if not self.config_file.endswith(".yaml"):
            raise ValueError("Only YAML files are supported.")

    def load(self) -> dict:
        """Load the configuration from the specified YAML file."""
        try:
            with open(self.config_file) as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            print(f"Failed to load config: {e}")
            return {}


@dataclass
class GetDataset:
    """A class to get a signed URL for a dataset stored in Google Cloud Storage (GCS)."""

    provider_name: str
    dataset_name: str

    def get_dataset_path(self) -> str:
        """Construct the GCS path for the dataset."""
        payload = {
            "company_name": self.provider_name,
            "target": self.dataset_name,
            # "expiration_minutes": 60  # or however long you want the URL to be valid
        }

        # Make a POST request to your endpoint
        try:
            response = requests.post(
                # "http://127.0.0.1:8000/generate-signed-url", json=payload)
                "https://fastapi-gcs-app-153945772792.northamerica-northeast2.run.app/generate-signed-url", json=payload)

            if response.status_code == 200:
                data = response.json()
                signed_url = data["signed_url"]
                return signed_url

            else:
                print("Error:", response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            print("Request failed:", str(e))
