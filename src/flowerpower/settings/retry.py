import os

# RETRY
MAX_RETRIES = int(os.getenv("FP_MAX_RETRIES", 1))
RETRY_DELAY = float(os.getenv("FP_RETRY_DELAY", 1.0))
JITTER_FACTOR = float(os.getenv("FP_JITTER_FACTOR", 0.1))
