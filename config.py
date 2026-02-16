# API Configuration
# Add your valid API keys here
VALID_API_KEYS = [
    "DEMO-KEY-12345",
    "YOUR-CUSTOM-KEY-HERE",
    "MOBILE-APP-KEY-2026"
]

# Or set environment variable
import os
if os.getenv('GANTT_API_KEY'):
    VALID_API_KEYS.append(os.getenv('GANTT_API_KEY'))
