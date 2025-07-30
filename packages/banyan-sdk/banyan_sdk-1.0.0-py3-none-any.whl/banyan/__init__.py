"""
Prompt Stack Manager Python SDK

A client SDK for logging real-world prompt usage to Prompt Stack Manager
and fetching prompts directly from the platform.
"""

import asyncio
import json
import time
import threading
import hashlib
from queue import Queue, Empty
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import requests
import logging

__version__ = "1.0.0"

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Represents a single prompt log entry"""
    prompt_id: Optional[str]
    prompt_name: Optional[str]
    version: Optional[str]
    branch_name: Optional[str]
    input: str
    output: str
    model: Optional[str]
    metadata: Dict[str, Any]
    duration_ms: Optional[int]
    timestamp: float
    experiment_id: Optional[str] = None
    experiment_version_id: Optional[str] = None

@dataclass 
class PromptData:
    """Represents a prompt fetched from the platform"""
    prompt_id: str
    name: str
    content: str
    version: str
    branch: str
    project: str
    enable_logging: bool

@dataclass
class ExperimentData:
    """Represents an active experiment"""
    experiment_id: str
    prompt_id: str
    prompt_name: str
    content: str
    version: str
    branch: str
    project: str
    experiment_version_id: str
    sticky_type: str
    sticky_value: str
    is_running: bool

class PromptStackLogger:
    """
    Main client for logging prompt usage to Prompt Stack Manager
    
    Features:
    - Asynchronous/background-safe logging
    - Automatic retry logic with exponential backoff
    - Local queue for offline resilience
    - API key authentication
    - Direct prompt fetching from platform
    - Project-level binding support
    - Experiment management
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://banyan-smpms.ondigitalocean.app",
        project_id: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        queue_size: int = 1000,
        flush_interval: float = 5.0,
        background_thread: bool = True
    ):
        """
        Initialize the Prompt Stack Logger
        
        Args:
            api_key: Your Prompt Stack Manager API key
            base_url: Base URL of your Prompt Stack Manager instance
            project_id: Optional project ID for project-bound API keys
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Initial delay between retries (exponential backoff)
            queue_size: Maximum size of the local log queue
            flush_interval: How often to flush queued logs (seconds)
            background_thread: Whether to process logs in background thread
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Queue for background processing
        self.log_queue = Queue(maxsize=queue_size)
        self.background_thread_enabled = background_thread
        self.background_thread = None
        self.shutdown_event = threading.Event()
        
        # Cache for fetched prompts
        self._prompt_cache = {}
        
        # Current active experiment
        self._active_experiment: Optional[ExperimentData] = None
        
        # Statistics
        self.stats = {
            'logs_queued': 0,
            'logs_sent': 0,
            'logs_failed': 0,
            'retries_attempted': 0,
            'prompts_fetched': 0,
            'cache_hits': 0,
            'experiments_set': 0
        }
        
        if background_thread:
            self._start_background_thread(flush_interval)
    
    def _start_background_thread(self, flush_interval: float):
        """Start the background thread for processing logs"""
        def background_worker():
            while not self.shutdown_event.is_set():
                try:
                    # Process queued logs
                    logs_to_send = []
                    
                    # Collect logs from queue (non-blocking)
                    try:
                        while len(logs_to_send) < 50:  # Batch size limit
                            log_entry = self.log_queue.get_nowait()
                            logs_to_send.append(log_entry)
                    except Empty:
                        pass
                    
                    # Send logs if any collected
                    if logs_to_send:
                        for log_entry in logs_to_send:
                            self._send_log_with_retry(log_entry)
                    
                    # Wait for next flush interval
                    self.shutdown_event.wait(flush_interval)
                    
                except Exception as e:
                    logger.error(f"Background worker error: {e}")
                    self.shutdown_event.wait(1.0)  # Brief pause on error
        
        self.background_thread = threading.Thread(target=background_worker, daemon=True)
        self.background_thread.start()
    
    def get_prompt(
        self,
        name: str,
        version: Optional[str] = None,
        branch: str = "main",
        use_cache: bool = True,
        project_id: Optional[str] = None
    ) -> Optional[PromptData]:
        """
        Fetch a prompt from the platform by name
        
        Args:
            name: Name of the prompt
            version: Specific version to fetch (if None, gets latest from branch)
            branch: Branch to fetch from (default: "main")
            use_cache: Whether to use cached prompt data
            project_id: Optional project ID to filter prompts (overrides configured project_id)
            
        Returns:
            PromptData object or None if not found
        """
        try:
            # Use specified project_id or fall back to configured one
            effective_project_id = project_id or self.project_id
            
            # Create cache key including project for proper caching
            cache_key = f"{name}:{version or 'latest'}:{branch}:{effective_project_id or 'org'}"
            
            if use_cache and cache_key in self._prompt_cache:
                cached_prompt = self._prompt_cache[cache_key]
                self.stats['cache_hits'] += 1
                return cached_prompt
            
            # Build request URL and params for regular prompt fetch
            url = f"{self.base_url}/api/logs/prompt/{name}"
            params = {'branch': branch}
            if version:
                params['version'] = version
                
            headers = {'X-API-Key': self.api_key}
            if effective_project_id:
                headers['X-Project-Id'] = effective_project_id
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 404:
                logger.warning(f"Prompt '{name}' not found")
                return None
            elif response.status_code != 200:
                logger.error(f"Failed to fetch prompt: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            prompt_data = PromptData(
                prompt_id=data['prompt_id'],
                name=data['name'],
                content=data['content'],
                version=data['version'],
                branch=data['branch'],
                project=data['project'],
                enable_logging=data['enable_logging']
            )
            
            # Cache the result
            if use_cache:
                self._prompt_cache[cache_key] = prompt_data
                
            self.stats['prompts_fetched'] += 1
            return prompt_data
            
        except Exception as e:
            logger.error(f"Error fetching prompt '{name}': {e}")
            return None

    def experiment(
        self, 
        experiment_id: str, 
        sticky_context: Optional[Dict[str, str]] = None,
        input_text: Optional[str] = None
    ) -> ExperimentData:
        """
        Set up experiment routing for subsequent prompt fetches and logging
        
        Args:
            experiment_id: ID of the experiment to participate in
            sticky_context: Dict with experiment routing context. Only required for user_id sticky type.
                          For input_hash sticky type, it will be auto-calculated from input_text.
            input_text: The input text (required for input_hash sticky type experiments)
            
        Returns:
            ExperimentData object with the routed prompt version
            
        Raises:
            RuntimeError: If experiment is not running or sticky context is missing
        """
        try:
            # First, get experiment details to understand sticky type
            experiment_info = self._get_experiment_info(experiment_id)
            if not experiment_info:
                raise RuntimeError(f"Experiment {experiment_id} not found")
            
            if experiment_info['status'] != 'running':
                raise RuntimeError(f"Experiment {experiment_id} is not running (status: {experiment_info['status']})")
            
            sticky_type = experiment_info['sticky_type']
            sticky_value = None
            
            # Handle different sticky types
            if sticky_type == 'user_id':
                if not sticky_context or 'user_id' not in sticky_context:
                    raise RuntimeError("user_id must be provided in sticky_context for user_id sticky type experiments")
                sticky_value = sticky_context['user_id']
            elif sticky_type == 'input_hash':
                if not input_text:
                    raise RuntimeError("input_text must be provided for input_hash sticky type experiments")
                sticky_value = hashlib.md5(input_text.encode()).hexdigest()[:16]
            elif sticky_type == 'session_id':
                # Auto-generate session_id if not provided
                if sticky_context and 'session_id' in sticky_context:
                    sticky_value = sticky_context['session_id']
                else:
                    # Generate a session ID based on experiment and time
                    session_seed = f"{experiment_id}:{int(time.time() / 3600)}"  # hourly sessions
                    sticky_value = hashlib.md5(session_seed.encode()).hexdigest()[:16]
            else:
                raise RuntimeError(f"Unsupported sticky type: {sticky_type}")
            
            # Route the experiment
            routing_result = self._route_experiment_by_id(experiment_id, sticky_type, sticky_value)
            if not routing_result:
                raise RuntimeError(f"Failed to route experiment {experiment_id}")
            
            # Create experiment data
            experiment_data = ExperimentData(
                experiment_id=experiment_id,
                prompt_id=routing_result['prompt_id'],
                prompt_name=experiment_info.get('prompt_name', 'Unknown'),
                content=routing_result['content'],
                version=routing_result['version_number'],
                branch=experiment_info.get('branch', 'main'),  # Use default if not available
                project=experiment_info.get('project', experiment_info.get('project_id', 'default')),
                experiment_version_id=routing_result['experiment_version_id'],
                sticky_type=sticky_type,
                sticky_value=sticky_value,
                is_running=True
            )
            
            # Set as active experiment
            self._active_experiment = experiment_data
            self.stats['experiments_set'] += 1
            
            logger.info(f"Set experiment {experiment_id} with sticky {sticky_type}={sticky_value}")
            return experiment_data
            
        except Exception as e:
            logger.error(f"Error setting up experiment {experiment_id}: {e}")
            raise

    def _get_experiment_info(self, experiment_id: str) -> Optional[Dict]:
        """Get experiment information"""
        try:
            url = f"{self.base_url}/api/experiments/{experiment_id}"
            headers = {'X-API-Key': self.api_key}
            if self.project_id:
                headers['X-Project-Id'] = self.project_id
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get experiment info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting experiment info: {e}")
            return None

    def _route_experiment_by_id(self, experiment_id: str, sticky_key: str, sticky_value: str) -> Optional[Dict]:
        """
        Route experiment using experiment ID directly
        """
        try:
            url = f"{self.base_url}/api/experiments/route"
            payload = {
                'experimentId': experiment_id,  # Use experiment ID directly
                'stickyKey': sticky_key,
                'stickyValue': sticky_value,
                'apiKey': self.api_key
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.warning(f"Experiment routing failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in experiment routing: {e}")
            return None

    def log_prompt(
        self,
        input: str,
        output: str,
        prompt_data: Optional[PromptData] = None,
        prompt_id: Optional[str] = None,
        prompt_name: Optional[str] = None,
        version: Optional[str] = None,
        branch_name: Optional[str] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        blocking: bool = False
    ) -> bool:
        """
        Log a prompt execution
        
        Args:
            input: The input text sent to the model
            output: The output text received from the model
            prompt_data: PromptData object from get_prompt() (preferred method)
            prompt_id: ID of the prompt in Prompt Stack Manager (optional)
            prompt_name: Name of the prompt (optional)
            version: Version of the prompt used (optional)
            branch_name: Branch name of the prompt (optional)
            model: Name of the model used (optional)
            metadata: Additional metadata (user_id, session_id, etc.)
            duration_ms: Execution time in milliseconds (optional)
            blocking: If True, send immediately and block until complete
            
        Returns:
            bool: True if successfully queued/sent, False otherwise
        """
        try:
            # Check if there's an active experiment and fail if it's not running
            experiment_context = None
            if self._active_experiment:
                if not self._active_experiment.is_running:
                    logger.error("Cannot log prompt: active experiment is not running")
                    return False
                
                experiment_context = {
                    'experiment_id': self._active_experiment.experiment_id,
                    'experiment_version_id': self._active_experiment.experiment_version_id,
                    'sticky_context': {
                        self._active_experiment.sticky_type: self._active_experiment.sticky_value
                    }
                }
                
                # Use experiment data if no prompt_data provided
                if not prompt_data:
                    prompt_id = self._active_experiment.prompt_id
                    prompt_name = self._active_experiment.prompt_name
                    version = self._active_experiment.version
                    branch_name = self._active_experiment.branch
            
            # If prompt_data is provided, extract information from it
            if prompt_data:
                prompt_id = prompt_data.prompt_id
                prompt_name = prompt_data.name
                version = prompt_data.version
                branch_name = prompt_data.branch
            
            # Prepare metadata
            combined_metadata = metadata.copy() if metadata else {}
            
            log_entry = LogEntry(
                prompt_id=prompt_id,
                prompt_name=prompt_name,
                version=version,
                branch_name=branch_name,
                input=input,
                output=output,
                model=model,
                metadata=combined_metadata,
                duration_ms=duration_ms,
                timestamp=time.time()
            )
            
            # Add experiment context for sending to API
            if experiment_context:
                log_entry.experiment_id = experiment_context.get('experiment_id')
                log_entry.experiment_version_id = experiment_context.get('experiment_version_id')
                # Store sticky context as additional attributes
                setattr(log_entry, '_sticky_context', experiment_context.get('sticky_context', {}))
            
            if blocking or not self.background_thread_enabled:
                # Send immediately
                return self._send_log_with_retry(log_entry)
            else:
                # Queue for background processing
                try:
                    self.log_queue.put_nowait(log_entry)
                    self.stats['logs_queued'] += 1
                    return True
                except:
                    # Queue is full, try to send immediately as fallback
                    logger.warning("Log queue full, sending immediately")
                    return self._send_log_with_retry(log_entry)
                    
        except Exception as e:
            logger.error(f"Error logging prompt: {e}")
            return False
    
    def _send_log_with_retry(self, log_entry: LogEntry) -> bool:
        """Send a log entry with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                success = self._send_log(log_entry)
                if success:
                    self.stats['logs_sent'] += 1
                    return True
                    
            except Exception as e:
                logger.warning(f"Log send attempt {attempt + 1} failed: {e}")
                
            if attempt < self.max_retries:
                self.stats['retries_attempted'] += 1
                # Exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)
        
        self.stats['logs_failed'] += 1
        logger.error(f"Failed to send log after {self.max_retries + 1} attempts")
        return False
    
    def _send_log(self, log_entry: LogEntry) -> bool:
        """Send a single log entry to the API"""
        url = f"{self.base_url}/api/logs/prompt-usage"
        
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Include project header if configured
        if self.project_id:
            headers['X-Project-Id'] = self.project_id
        
        payload = {
            'prompt_id': log_entry.prompt_id,
            'prompt_name': log_entry.prompt_name,
            'version': log_entry.version,
            'branch_name': log_entry.branch_name,
            'input': log_entry.input,
            'output': log_entry.output,
            'model': log_entry.model,
            'metadata': log_entry.metadata,
            'duration_ms': log_entry.duration_ms
        }
        
        # Add experiment context if available
        if log_entry.experiment_id:
            payload['experiment_id'] = log_entry.experiment_id
        if log_entry.experiment_version_id:
            payload['experiment_version_id'] = log_entry.experiment_version_id
        
        # Add sticky context for experiment routing
        if hasattr(log_entry, '_sticky_context') and log_entry._sticky_context:
            sticky_context = log_entry._sticky_context
            for key in ['user_id', 'session_id', 'input_hash', 'customer_id']:
                if key in sticky_context:
                    payload['sticky_key'] = key
                    payload['sticky_value'] = sticky_context[key]
                    break
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 201:
            return True
        elif response.status_code == 401:
            logger.error("Invalid API key")
            return False
        else:
            response.raise_for_status()
            return False
    
    def flush(self, timeout: float = 30.0) -> bool:
        """
        Flush all queued logs immediately
        
        Args:
            timeout: Maximum time to wait for flush completion
            
        Returns:
            bool: True if all logs were flushed successfully
        """
        if not self.background_thread_enabled:
            return True
        
        start_time = time.time()
        initial_queue_size = self.log_queue.qsize()
        
        while self.log_queue.qsize() > 0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        remaining = self.log_queue.qsize()
        if remaining > 0:
            logger.warning(f"Flush timeout: {remaining} logs still queued")
            return False
        
        logger.info(f"Flushed {initial_queue_size} logs successfully")
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get logging statistics"""
        stats = self.stats.copy()
        stats['queue_size'] = self.log_queue.qsize()
        return stats
    
    def shutdown(self, timeout: float = 30.0):
        """
        Gracefully shutdown the logger
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        if self.background_thread_enabled and self.background_thread:
            logger.info("Shutting down Prompt Stack Logger...")
            
            # Flush remaining logs
            self.flush(timeout)
            
            # Stop background thread
            self.shutdown_event.set()
            self.background_thread.join(timeout)
            
            logger.info("Prompt Stack Logger shutdown complete")

# Global logger instance
_global_logger: Optional[PromptStackLogger] = None

def configure(
    api_key: str, 
    base_url: str = "https://banyan-smpms.ondigitalocean.app",
    project_id: Optional[str] = None,
    **kwargs
):
    """
    Configure the global Prompt Stack logger
    
    Args:
        api_key: Your Prompt Stack Manager API key
        base_url: Base URL of your Prompt Stack Manager instance  
        project_id: Optional project ID for project-bound API keys
        **kwargs: Additional arguments passed to PromptStackLogger
    """
    global _global_logger
    _global_logger = PromptStackLogger(
        api_key=api_key, 
        base_url=base_url, 
        project_id=project_id,
        **kwargs
    )

def get_prompt(
    name: str,
    version: Optional[str] = None,
    branch: str = "main",
    use_cache: bool = True,
    project_id: Optional[str] = None
) -> Optional[PromptData]:
    """
    Fetch a prompt from the platform by name (without experiment routing)
    
    Args:
        name: Name of the prompt
        version: Specific version to fetch (if None, gets latest from branch)
        branch: Branch to fetch from (default: "main")
        use_cache: Whether to use cached prompt data
        project_id: Optional project ID to filter prompts (overrides configured project_id)
            
    Returns:
        PromptData object or None if not found
    """
    if _global_logger is None:
        raise RuntimeError("Must call configure() first")
    return _global_logger.get_prompt(name, version, branch, use_cache, project_id)

def experiment(
    experiment_id: str, 
    sticky_context: Optional[Dict[str, str]] = None,
    input_text: Optional[str] = None
) -> ExperimentData:
    """
    Set up experiment routing for subsequent prompt fetches and logging
    
    Args:
        experiment_id: ID of the experiment to participate in
        sticky_context: Dict with experiment routing context. Only required for user_id sticky type.
                      For input_hash sticky type, it will be auto-calculated from input_text.
        input_text: The input text (required for input_hash sticky type experiments)
        
    Returns:
        ExperimentData object with the routed prompt version
        
    Raises:
        RuntimeError: If experiment is not running or sticky context is missing
    """
    if _global_logger is None:
        raise RuntimeError("Must call configure() first")
    return _global_logger.experiment(experiment_id, sticky_context, input_text)

def log_prompt(
    input: str,
    output: str,
    prompt_data: Optional[PromptData] = None,
    prompt_id: Optional[str] = None,
    prompt_name: Optional[str] = None,
    version: Optional[str] = None,
    branch_name: Optional[str] = None,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[int] = None,
    blocking: bool = False
) -> bool:
    """
    Log a prompt execution
    
    Args:
        input: The input text sent to the model
        output: The output text received from the model
        prompt_data: PromptData object from get_prompt() (preferred method)
        prompt_id: ID of the prompt in Prompt Stack Manager (optional)
        prompt_name: Name of the prompt (optional)
        version: Version of the prompt used (optional)
        branch_name: Branch name of the prompt (optional)
        model: Name of the model used (optional)
        metadata: Additional metadata (user_id, session_id, etc.)
        duration_ms: Execution time in milliseconds (optional)
        blocking: If True, send immediately and block until complete
        
    Returns:
        bool: True if successfully queued/sent, False otherwise
    """
    if _global_logger is None:
        raise RuntimeError("Must call configure() first")
    return _global_logger.log_prompt(
        input=input,
        output=output,
        prompt_data=prompt_data,
        prompt_id=prompt_id,
        prompt_name=prompt_name,
        version=version,
        branch_name=branch_name,
        model=model,
        metadata=metadata,
        duration_ms=duration_ms,
        blocking=blocking
    )

def flush(timeout: float = 30.0) -> bool:
    """Flush all queued logs using the global logger"""
    if _global_logger is None:
        return True
    return _global_logger.flush(timeout)

def get_stats() -> Dict[str, int]:
    """Get logging statistics from the global logger"""
    if _global_logger is None:
        return {}
    return _global_logger.get_stats()

def shutdown(timeout: float = 30.0):
    """Shutdown the global logger"""
    if _global_logger is not None:
        _global_logger.shutdown(timeout)

# Alias for the main logging function to match the user's example
log = log_prompt 