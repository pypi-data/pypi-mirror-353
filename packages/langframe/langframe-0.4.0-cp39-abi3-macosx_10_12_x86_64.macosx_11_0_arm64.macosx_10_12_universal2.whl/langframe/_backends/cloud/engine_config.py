from __future__ import annotations

import os
import pickle  # nosec: B403

from langframe._constants import API_KEY_SUFFIX
from langframe.api.session.config import (
    OPEN_AI_COMPLETIONS_MODEL_CONFIG,
    OPEN_AI_EMBEDDING_MODEL_CONFIG,
    SessionConfig,
)


class CloudSessionConfig:
    """
    Configuration required for cloud session

    Attributes:
        session_config (SessionConfig): The session configuration created by the user.
        model_api_keys (Dict[str, str]): A dictionary of model API keys.

    Upon initialization, will read the API keys required for the SemanticConfig from the environment variables
    """

    def __init__(self, session_config: SessionConfig):
        self.model_api_keys = {}
        self.session_config = session_config
        self.session_config.cloud = None

        # Read keys from environment variables ending with _API_KEY
        env_keys = {
            key: value
            for key, value in os.environ.items()
            if key.endswith(API_KEY_SUFFIX)
        }

        # Collect the keys required for the configured language models
        completions_model_name = self.session_config.semantic.language_model.model_name
        if completions_model_name in OPEN_AI_COMPLETIONS_MODEL_CONFIG:
            completions_api_key = f"OPENAI{API_KEY_SUFFIX}"
        else:
            raise ValueError(f"Unsupported language model: {completions_model_name}")

        if completions_api_key not in env_keys.keys():
            raise ValueError(
                f"{completions_api_key} is not set. Required to use {completions_model_name}."
            )
        self.model_api_keys[completions_api_key] = env_keys[completions_api_key]

        if self.session_config.semantic.embedding_model:
            embeddings_model_name = (
                self.session_config.semantic.embedding_model.model_name
            )
            if embeddings_model_name in OPEN_AI_EMBEDDING_MODEL_CONFIG:
                embeddings_api_key = f"OPENAI{API_KEY_SUFFIX}"
            else:
                raise ValueError(
                    f"Unsupported embedding model: {embeddings_model_name}"
                )

            if embeddings_api_key not in env_keys.keys():
                raise ValueError(
                    f"{embeddings_api_key} is not set. Required to use {embeddings_model_name}."
                )
            self.model_api_keys[embeddings_api_key] = env_keys[embeddings_api_key]

    @staticmethod
    def deserialize(data: bytes) -> CloudSessionConfig:
        return pickle.loads(data)  # nosec: B301

    def serialize(self) -> bytes:
        return pickle.dumps(self)
