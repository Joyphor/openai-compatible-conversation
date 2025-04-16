"""Memobase client for OpenAI Compatible Conversation."""
from __future__ import annotations

import asyncio
from typing import Any, Optional

from memobase import AsyncMemobaseClient, ChatBlob

from homeassistant.core import HomeAssistant

from .const import LOGGER

class MemobaseManager:
    """Class to manage Memobase interactions."""

    def __init__(
        self, 
        hass: HomeAssistant,
        url: str, 
        api_key: str, 
        user_id: Optional[str] = None
    ) -> None:
        """Initialize the Memobase manager.
        
        Args:
            hass: HomeAssistant instance
            url: Memobase server URL
            api_key: Memobase API key
            user_id: Optional user ID to use
        """
        self.hass = hass
        self.client = AsyncMemobaseClient(project_url=url, api_key=api_key)
        self.user = None
        self.user_id = user_id
        self._connected = False
        self._connection_lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Connect to Memobase and initialize user.
        
        Returns:
            True if connection was successful, False otherwise
        """
        if self._connected:
            return True
            
        async with self._connection_lock:
            if self._connected:  # Check again inside lock
                return True
                
            try:
                # Test connection
                if not await self.client.ping():
                    LOGGER.error("Failed to connect to Memobase")
                    return False
                    
                # Get or create user
                if self.user_id:
                    try:
                        self.user = await self.client.get_user(self.user_id)
                        LOGGER.info("Connected to existing Memobase user: %s", self.user_id)
                    except Exception as err:
                        LOGGER.warning(
                            "User ID %s not found, creating new user: %s", 
                            self.user_id, err
                        )
                        self.user_id = await self.client.add_user({"source": "homeassistant"})
                        self.user = await self.client.get_user(self.user_id)
                        LOGGER.info("Created new Memobase user: %s", self.user_id)
                else:
                    self.user_id = await self.client.add_user({"source": "homeassistant"})
                    self.user = await self.client.get_user(self.user_id)
                    LOGGER.info("Created new Memobase user: %s", self.user_id)
                
                self._connected = True
                return True
            except Exception as err:
                LOGGER.error("Error connecting to Memobase: %s", err)
                return False

    async def store_conversation(
        self, 
        user_message: str, 
        assistant_response: str, 
        assistant_name: str = "Assistant"
    ) -> bool:
        """Store a conversation exchange in Memobase.
        
        Args:
            user_message: The user's message
            assistant_response: The assistant's response
            assistant_name: Name of the assistant for the alias
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected and not await self.connect():
            return False
            
        messages = [
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "content": assistant_response,
                "alias": assistant_name
            }
        ]
        
        try:
            await self.user.insert(ChatBlob(messages=messages))
            LOGGER.debug("Stored conversation in Memobase")
            return True
        except Exception as err:
            LOGGER.error("Error storing conversation in Memobase: %s", err)
            return False

    async def get_user_profile(
        self, 
        max_tokens: int = 500, 
        prefer_topics: Optional[list[str]] = None
    ) -> str:
        """Get the user profile as a formatted string for prompts.
        
        Args:
            max_tokens: Maximum number of tokens to include
            prefer_topics: List of topics to prioritize
            
        Returns:
            Formatted user profile string or empty string on error
        """
        if not self._connected and not await self.connect():
            return ""
            
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                context = await self.user.context(
                    max_token_size=max_tokens, 
                    prefer_topics=prefer_topics
                )
                return context
            except Exception as err:
                retry_count += 1
                LOGGER.warning(
                    "Error retrieving user profile (attempt %s/%s): %s", 
                    retry_count, max_retries, err
                )
                if retry_count >= max_retries:
                    return ""
                await asyncio.sleep(1)  # Brief delay before retry

    async def flush_buffer(self) -> bool:
        """Flush the Memobase buffer to process conversations.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connected and not await self.connect():
            return False
            
        try:
            await self.user.flush()
            LOGGER.info("Flushed Memobase buffer for user: %s", self.user_id)
            return True
        except Exception as err:
            LOGGER.error("Error flushing Memobase buffer: %s", err)
            return False
    
    def get_user_id(self) -> Optional[str]:
        """Get the Memobase user ID.
        
        Returns:
            The user ID or None if not connected
        """
        return self.user_id if self._connected else None