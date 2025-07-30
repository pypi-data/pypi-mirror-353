"""
API Key Manager for handling multiple Gemini API keys with rate limiting and rotation.
"""

import time
import logging
import threading
from collections import deque
from typing import List, Dict, Optional

from ..exceptions import APIKeyError

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages multiple API keys with rate limiting and rotation.
    
    Features:
    - Rotates through multiple API keys to avoid rate limits
    - Tracks usage of each key to respect rate limits
    - Provides cooldown periods for keys that hit rate limits
    - Falls back to other keys when one is exhausted
    """
    
    def __init__(self, api_keys: List[str], calls_per_key_per_minute: int = 15, cooldown_period: int = 60):
        """
        Initialize the API key manager
        
        Args:
            api_keys: List of API keys
            calls_per_key_per_minute: Maximum calls allowed per key per minute
            cooldown_period: Cooldown period in seconds after a key hits rate limit
            
        Raises:
            APIKeyError: If no API keys are provided
        """
        if not api_keys:
            raise APIKeyError("No API keys provided")
            
        self.api_keys = api_keys
        self.calls_per_key_per_minute = calls_per_key_per_minute
        self.cooldown_period = cooldown_period
        self.key_index = 0
        self.key_usage: Dict[str, deque] = {key: deque(maxlen=60) for key in api_keys}
        self.key_health: Dict[str, bool] = {key: True for key in api_keys}
        self._lock = threading.Lock()
        
        logger.info(f"Initialized API Key Manager with {len(api_keys)} keys")
        logger.info(f"Rate limit: {calls_per_key_per_minute} calls per key per minute")
        logger.info(f"Cooldown period: {cooldown_period} seconds")
    
    def get_next_available_key(self) -> str:
        """
        Get the next available API key with respect to rate limits
        
        Returns:
            A valid API key that hasn't exceeded rate limits
            
        Raises:
            APIKeyError: If all keys are exhausted and cooldown fails
        """
        with self._lock:
            start_index = self.key_index
            
            while True:
                current_key = self.api_keys[self.key_index]
                current_time = time.time()
                
                # Skip unhealthy keys
                if not self.key_health[current_key]:
                    logger.debug(f"Skipping unhealthy key: {self._mask_key(current_key)}")
                    self.key_index = (self.key_index + 1) % len(self.api_keys)
                    
                    # If we've checked all keys and circled back, wait for the cooldown period
                    if self.key_index == start_index:
                        logger.warning("All keys are unhealthy! Waiting for cooldown period...")
                        time.sleep(self.cooldown_period)
                        
                        # Reset health status for all keys
                        for key in self.api_keys:
                            self.key_health[key] = True
                    
                    continue
                
                # Remove timestamps older than 1 minute
                while self.key_usage[current_key] and current_time - self.key_usage[current_key][0] > 60:
                    self.key_usage[current_key].popleft()
                
                # Check if this key has capacity
                if len(self.key_usage[current_key]) < self.calls_per_key_per_minute:
                    # This key is available
                    self.key_usage[current_key].append(current_time)
                    key_to_return = current_key
                    
                    # Move to next key for future calls
                    self.key_index = (self.key_index + 1) % len(self.api_keys)
                    
                    return key_to_return
                
                # Move to next key
                self.key_index = (self.key_index + 1) % len(self.api_keys)
                
                # If we've checked all keys and circled back, we need to wait
                if self.key_index == start_index:
                    # Find the key that will be available soonest
                    min_wait = float('inf')
                    for key in self.api_keys:
                        if self.key_usage[key] and self.key_health[key]:
                            # Calculate when the oldest call will expire
                            wait_time = 60 - (current_time - self.key_usage[key][0])
                            min_wait = min(min_wait, wait_time)
                    
                    # Wait a bit longer than the minimum wait time to be safe
                    wait_time = max(min_wait + 0.5, 1)
                    logger.info(f"All API keys at rate limit. Waiting {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
    
    def mark_key_unhealthy(self, key: str) -> None:
        """
        Mark a key as unhealthy, e.g., after it hit a rate limit
        
        Args:
            key: The API key to mark as unhealthy
        """
        if key not in self.key_health:
            logger.warning(f"Attempted to mark unknown key as unhealthy: {self._mask_key(key)}")
            return
            
        self.key_health[key] = False
        logger.warning(f"Marked key {self._mask_key(key)} as unhealthy")
        
        # Schedule key to be marked healthy again after cooldown period
        def reset_key_health():
            time.sleep(self.cooldown_period)
            self.key_health[key] = True
            logger.info(f"Key {self._mask_key(key)} is healthy again after cooldown")
        
        # Start a thread to reset the key health after cooldown
        threading.Thread(target=reset_key_health, daemon=True).start()
    
    def get_key_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all API keys
        
        Returns:
            Dictionary with key statistics
        """
        stats = {}
        current_time = time.time()
        
        for key in self.api_keys:
            # Count recent calls (last minute)
            recent_calls = sum(1 for timestamp in self.key_usage[key] 
                             if current_time - timestamp <= 60)
            
            stats[self._mask_key(key)] = {
                'healthy': self.key_health[key],
                'recent_calls': recent_calls,
                'capacity_remaining': max(0, self.calls_per_key_per_minute - recent_calls),
                'total_calls': len(self.key_usage[key])
            }
            
        return stats
    
    def reset_all_keys(self) -> None:
        """Reset all keys to healthy status and clear usage history"""
        with self._lock:
            for key in self.api_keys:
                self.key_health[key] = True
                self.key_usage[key].clear()
            self.key_index = 0
        logger.info("Reset all API keys to healthy status")
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for logging purposes"""
        if len(key) <= 8:
            return "****"
        return key[:4] + "****" + key[-4:]
    
    @property
    def effective_rate_limit(self) -> int:
        """Calculate the effective rate limit across all healthy keys"""
        healthy_keys = sum(1 for key in self.api_keys if self.key_health[key])
        return healthy_keys * self.calls_per_key_per_minute
    
    @property
    def total_keys(self) -> int:
        """Get total number of API keys"""
        return len(self.api_keys)
    
    @property
    def healthy_keys(self) -> int:
        """Get number of healthy API keys"""
        return sum(1 for key in self.api_keys if self.key_health[key])
