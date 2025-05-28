"""
AIENERGY Backend
---------------
A Flask-based backend for analyzing energy invoices using OCR and LLM technologies.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize package
__version__ = '0.1.0'
