"""Constants for the OpenAI Compatible Conversation integration."""

import logging

DOMAIN = "openai_compatible_conversation"
LOGGER = logging.getLogger(__package__)

CONF_RECOMMENDED = "recommended"
CONF_PROMPT = "prompt"
CONF_CHAT_MODEL = "chat_model"
RECOMMENDED_CHAT_MODEL = "mistral-small-24b-instruct-2501"
CONF_MAX_TOKENS = "max_tokens"
RECOMMENDED_MAX_TOKENS = 8.192
CONF_TOP_P = "top_p"
RECOMMENDED_TOP_P = 1.0
CONF_TEMPERATURE = "temperature"
RECOMMENDED_TEMPERATURE = 0.5
CONF_BASE_URL = "base_url"
RECOMMENDED_BASE_URL = "http://10.101.100.5:1234/v1"

# Memobase configuration constants
CONF_MEMOBASE_ENABLED = "memobase_enabled"
CONF_MEMOBASE_URL = "memobase_url"
CONF_MEMOBASE_API_KEY = "memobase_api_key"
CONF_MEMOBASE_USER_ID = "memobase_user_id"

# Default Memobase settings
DEFAULT_MEMOBASE_URL = "http://10.101.100.5:8019"
DEFAULT_MEMOBASE_API_KEY = "secret"