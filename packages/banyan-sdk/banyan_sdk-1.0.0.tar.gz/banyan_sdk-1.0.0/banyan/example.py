#!/usr/bin/env python3
"""
Banyan SDK Usage Examples

This file demonstrates how to use the Banyan SDK for managing, versioning,
and A/B testing your LLM prompts in production.

Examples included:
1. Basic Configuration and Setup
2. Simple Prompt Fetching and Logging
3. Experiment-based Routing
4. Error Handling Best Practices
5. Advanced Configuration Options
6. Different Sticky Context Strategies
7. Statistics and Monitoring
"""

import os
import time
import hashlib
import logging
from typing import Optional, Dict, Any

# Import the Banyan SDK
import banyan

# Configure logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def basic_setup():
    """
    Example 1: Basic SDK Configuration and Setup
    
    This shows the minimal setup required to start using Banyan SDK.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Setup and Configuration")
    print("="*60)
    
    # Method 1: Configure with environment variables (recommended for production)
    # Set environment variable: export BANYAN_API_KEY=psk_your_api_key_here
    api_key = os.getenv('BANYAN_API_KEY')
    
    if not api_key:
        print("BANYAN_API_KEY not set. Using demo key for example.")
        api_key = "psk_demo_key_replace_with_real_key"
    
    try:
        # Configure the SDK
        banyan.configure(
            api_key=api_key,
            project_id="demo-project",  # Optional: for project-specific prompts
            max_retries=3,
            background_thread=True
        )
        
        stats = banyan.get_stats()
        print(f"   Initial stats: {stats}")
        
    except Exception as e:
        print(f"Configuration failed: {e}")

def basic_prompt_usage():
    """
    Example 2: Basic Prompt Fetching and Logging
    
    This demonstrates the core workflow: fetch prompt -> use with model -> log usage
    """
    
    try:
        # 1. Fetch a prompt
        print("Fetching prompt...")
        prompt_data = banyan.get_prompt(
            name="welcome-message",
            branch="main",
            use_cache=True
        )
        
        if not prompt_data:
            print("Prompt not found. Creating a demo prompt for this example.")
            # In real usage, you'd create the prompt in your Banyan dashboard
            return
        
        print(f"✅ Fetched prompt: {prompt_data.name}")
        print(f"   Version: {prompt_data.version}")
        print(f"   Branch: {prompt_data.branch}")
        print(f"   Content preview: {prompt_data.content[:100]}...")
        
        # 2. Simulate using the prompt with your model
        user_input = "Hello! I'm new to your platform."
        
        # This is where you'd call your actual model (OpenAI, Anthropic, etc.)
        start_time = time.time()
        model_output = llm_call(prompt_data.content, user_input)
        duration_ms = int((time.time() - start_time) * 1000)
        
        
        # 3. Log the prompt usage
        print("Logging prompt usage...")
        success = banyan.log_prompt(
            input=user_input,
            output=model_output,
            prompt_data=prompt_data,  # Contains all prompt metadata
            model="gpt-4",
            duration_ms=duration_ms,
            metadata={
                "user_type": "new_user",
                "feature": "welcome_flow",
                "environment": "demo"
            }
        )
        
        if success:
            print("Usage logged successfully!")
        else:
            print("Logging queued for retry")
            
    except Exception as e:
        print(f"Error in basic usage: {e}")

def experiment_routing():
    """
    Example 3: A/B Testing with Experiment Routing
    
    This shows how to use experiments for A/B testing different prompt versions.
    """

    user_id = "a_unique_user_id_for_each_of_your_users"
    
    try:
        # Set up experiment routing with sticky user context
        print(f"etting up experiment for user: {user_id}")
        
        experiment_data = banyan.experiment(
            experiment_id="your_experiment_id",  # Your experiment ID
            sticky_context={"user_id": user_id},  # Consistent routing per user
            input_text=None  # Not needed for user_id sticky type
        )
        
        print(f"Experiment active!")
        print(f"Experiment ID: {experiment_data.experiment_id}")
        print(f"Using prompt version: {experiment_data.version}")
        print(f"Sticky value: {experiment_data.sticky_value}")
        print(f"Content preview: {experiment_data.content[:100]}...")
        
        # Use the experiment prompt version
        user_input = "I need help getting started"
        start_time = time.time()
        model_output = llm_call(experiment_data.content, user_input)
        duration_ms = int((time.time() - start_time) * 1000)
        
        
        # Log with experiment context (automatically included)
        success = banyan.log_prompt(
            input=user_input,
            output=model_output,
            model="gpt-4",
            duration_ms=duration_ms,
            metadata={
                "user_id": user_id,
                "experiment_active": True,
            }
        )
        
        if success:
            print("✅ Experiment usage logged with context!")
        
    except RuntimeError as e:
        print(f"No active experiment: {e}")

def Content_based_experiments():
    """
    Example 4: Content-based Experiments
    
    This demonstrates experiments that route based on the input text.
    """
    
    print("Content-based experiments")
    input_text = "What are your business hours?"
    try:
        experiment = banyan.experiment(
            experiment_id="content-based-test",
            input_text=input_text  # Automatically hashes the input text
        )
        print(f"Content sticky: {experiment.sticky_value}")
    except Exception as e:
        print(f"Content-based experiment not available: {e}")
    

def advanced_configuration():
    """
    Example 6: Advanced Configuration Options
    
    This demonstrates advanced SDK features and custom configurations.
    """
    
    # Custom logger instance
    print("Creating custom logger instance")
    try:
        from banyan import PromptStackLogger
        
        custom_logger = PromptStackLogger(
            api_key=os.getenv('BANYAN_API_KEY', 'demo_key'),
            base_url="https://banyan-smpms.ondigitalocean.app",
            project_id="custom-project",
            max_retries=5,
            retry_delay=2.0,
            queue_size=2000,
            flush_interval=10.0,
            background_thread=True
        )
        
        print("Custom logger created")
        
        # Use custom logger
        prompt_data = custom_logger.get_prompt("test-prompt")
        if prompt_data:
            print(f"Custom logger fetched: {prompt_data.name}")
        
        # Get custom logger stats
        stats = custom_logger.get_stats()
        print(f"Custom logger stats: {stats}")
        
    except Exception as e:
        print(f"Custom logger error: {e}")
    
    # Synchronous mode
    print("Testing synchronous mode")
    try:
        # Configure for synchronous operation
        banyan.configure(
            api_key=os.getenv('BANYAN_API_KEY', 'demo_key'),
            background_thread=False  # Disable background processing
        )
        
        # All operations will be synchronous
        success = banyan.log_prompt(
            input="Sync test",
            output="Sync response",
            prompt_name="sync-test",
            blocking=True
        )
        
        if success:
            print("Synchronous logging successful")
        
    except Exception as e:
        print(f"Synchronous mode error: {e}")


def main():
    """
    Run all examples in sequence
    """
    print("This script demonstrates various features of the Banyan SDK.")
    print("For production use, make sure to set your BANYAN_API_KEY environment variable.")
    
    try:
        # Run all examples
        basic_setup()
        basic_prompt_usage()
        experiment_routing()
        Content_based_experiments()
        advanced_configuration()
        
        # Final cleanup
        print("Shutting down...")
        
        try:
            banyan.shutdown(timeout=10)
            print("Banyan shutdown completed successfully")
        except Exception as e:
            print(f"Shutdown warning: {e}")
        
        print("All examples completed!")
        print("\nNext steps:")
        print("1. Get your API key from the Banyan dashboard")
        print("2. Set BANYAN_API_KEY environment variable")
        print("3. Create prompts in your Banyan project")
        print("4. Set up experiments for A/B testing")
        print("5. Integrate with your production LLM calls")
        
    except KeyboardInterrupt:
        print("Examples interrupted by user")
        banyan.shutdown(timeout=5)
    except Exception as e:
        print(f"Unexpected error: {e}")
        banyan.shutdown(timeout=5)

if __name__ == "__main__":
    main()
