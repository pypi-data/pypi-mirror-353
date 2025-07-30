"""
Session caching for PsonoAPI to avoid repeated authentication
"""
import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import nacl.encoding
import nacl.secret
from .datamodels import PsonoServerSession, PsonoServerConfig
import logging
import pickle

class SessionCache:
    """Manages cached Psono sessions for performance optimization"""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_minutes: int = 30):
        """
        Initialize session cache
        
        Args:
            cache_dir: Directory to store cache files (default: ~/.psono/cache)
            ttl_minutes: Time-to-live for cached sessions in minutes
        """
        self.cache_dir = cache_dir or (Path.home() / '.psono' / 'cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(minutes=ttl_minutes)
        self.logger = logging.getLogger(__name__)
        # Set restrictive permissions on cache directory
        try:
            self.cache_dir.chmod(0o700)
        except:
            pass  # Windows doesn't support chmod
    
    def _get_cache_key(self, config: PsonoServerConfig) -> str:
        """Generate unique cache key based on server config"""
        # Create a unique key from server URL and key ID
        key_parts = [
            config.server_url,
            config.key_id or '',
            str(config.ssl_verify)
        ]
        key_string = '|'.join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for a given cache key"""
        return self.cache_dir / f"session_{cache_key}.json"
    
    def _encrypt_session_data(self, data: Dict[str, Any], encryption_key: str) -> Dict[str, str]:
        """Encrypt sensitive session data"""
        # Use a portion of the API secret key as encryption key if available
        if len(encryption_key) >= 32:
            key = encryption_key[:32].encode()
        else:
            # Pad the key if it's too short
            key = encryption_key.ljust(32, 'x')[:32].encode()
        
        box = nacl.secret.SecretBox(key)
        
        # Encrypt the sensitive data
        encrypted = box.encrypt(pickle.dumps(data))
        
        return {
            'encrypted': nacl.encoding.HexEncoder.encode(encrypted).decode(),
            'version': '1.0'
        }
    
    def _decrypt_session_data(self, encrypted_data: Dict[str, str], encryption_key: str) -> Dict[str, Any]:
        """Decrypt session data"""
        if encrypted_data.get('version') != '1.0':
            raise ValueError("Unsupported cache version")
        
        # Use same key derivation as encryption
        if len(encryption_key) >= 32:
            key = encryption_key[:32].encode()
        else:
            key = encryption_key.ljust(32, 'x')[:32].encode()
        
        box = nacl.secret.SecretBox(key)
        
        # Decrypt the data
        encrypted = nacl.encoding.HexEncoder.decode(encrypted_data['encrypted'])
        decrypted = box.decrypt(encrypted)
        
        return pickle.loads(decrypted)
             
    def save_session(self, config: PsonoServerConfig, session: PsonoServerSession) -> None:
        """
        Save session to cache
        
        Args:
            config: Server configuration
            session: Active session to cache
        """
        
        if not session.logged_in or not session.token:
            self.logger.debug("Session not logged in or no token, not saving")
            return
        
        cache_key = self._get_cache_key(config)
        cache_file = self._get_cache_file(cache_key)
        
        # Prepare session data for caching
        session_data = {
            'token': session.token,
            'username': session.username,
            'public_key': session.public_key,
            'secret_key': session.secret_key,
            'user_public_key': session.user_public_key,
            'user_private_key': session.user_private_key,
            'user_secret_key': str(session.user_secret_key),
            'user_restricted': session.user_restricted,
            'timestamp': datetime.now().isoformat(),
            'server_url': config.server_url
        }
        
        # Remove None values
        session_data = {k: v for k, v in session_data.items() if v is not None}
        
        # Encrypt sensitive data using the API secret key
        encryption_key = config.secret_key or config.private_key or cache_key
        encrypted_data = self._encrypt_session_data(session_data, encryption_key)
        
        # Save to file with restrictive permissions
        cache_file.write_text(json.dumps(encrypted_data, indent=2))
        try:
            cache_file.chmod(0o600)
        except:
            pass  # Windows doesn't support chmod
    
    def load_session(self, config: PsonoServerConfig) -> Optional[PsonoServerSession]:
        """
        Load session from cache if valid
        
        Args:
            config: Server configuration
            
        Returns:
            Cached session or None if not found/expired
        """
        cache_key = self._get_cache_key(config)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            self.logger.debug("No psono session cache file exists, no session to load")
            return None
        
        try:
            # Read encrypted data
            encrypted_data = json.loads(cache_file.read_text())
            
            # Decrypt session data
            encryption_key = config.secret_key or config.private_key or cache_key
            session_data = self._decrypt_session_data(encrypted_data, encryption_key)
            
            # Check if session is expired
            timestamp = datetime.fromisoformat(session_data['timestamp'])
            if datetime.now() - timestamp > self.ttl:
                cache_file.unlink()  # Delete expired cache
                self.logger.debug("Psono Session Cache expired, removing.")
                return None
            
            # Verify server URL matches
            if session_data.get('server_url') != config.server_url:
                self.logger.debug("Psono Session server does not match")
                return None
            
            # Create session object
            session = PsonoServerSession(
                logged_in=True,
                server=config,
                token=session_data.get('token'),
                username=session_data.get('username'),
                public_key=session_data.get('public_key'),
                secret_key=session_data.get('secret_key'),
                user_public_key=session_data.get('user_public_key'),
                user_private_key=session_data.get('user_private_key'),
                user_secret_key=session_data.get('user_secret_key'),
                user_restricted=session_data.get('user_restricted')
            )
            self.logger.debug("Psono Session cache loaded")
            return session
            
        except Exception as e:
            # If anything goes wrong, delete the cache file
            try:
                cache_file.unlink()
            except:
                pass
            return None
    
    def invalidate_session(self, config: PsonoServerConfig) -> None:
        """
        Invalidate cached session
        
        Args:
            config: Server configuration
        """
        cache_key = self._get_cache_key(config)
        cache_file = self._get_cache_file(cache_key)
        
        if cache_file.exists():
            cache_file.unlink()
    
    def clear_all_sessions(self) -> None:
        """Clear all cached sessions"""
        for cache_file in self.cache_dir.glob("session_*.json"):
            try:
                cache_file.unlink()
            except:
                pass
    
    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from cache"""
        for cache_file in self.cache_dir.glob("session_*.json"):
            try:
                encrypted_data = json.loads(cache_file.read_text())
                # We can't decrypt without the key, but we can add a metadata section
                # For now, just check file modification time
                stat = cache_file.stat()
                age = time.time() - stat.st_mtime
                if age > self.ttl.total_seconds():
                    cache_file.unlink()
            except:
                # If we can't read the file, delete it
                try:
                    cache_file.unlink()
                except:
                    pass