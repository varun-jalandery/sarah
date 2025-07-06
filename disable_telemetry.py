"""
Telemetry disabling module - import this BEFORE importing chromadb
"""
import os
import sys

# Set environment variables to disable telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
os.environ['CHROMA_TELEMETRY_DISABLED'] = 'true'

# Monkey patch posthog to prevent the capture error
try:
    import posthog
    # Disable posthog completely
    posthog.disabled = True
    
    # Override the capture method to prevent errors
    original_capture = posthog.capture
    def safe_capture(*args, **kwargs):
        try:
            if len(args) == 3:
                # Fix the argument mismatch by restructuring the call
                user_id, event_name, properties = args
                return original_capture(user_id, event_name, properties, **kwargs)
            else:
                return original_capture(*args, **kwargs)
        except Exception:
            # Silently ignore telemetry errors
            pass
    
    posthog.capture = safe_capture
except ImportError:
    # posthog not available, which is fine
    pass

print("Telemetry disabled successfully")
