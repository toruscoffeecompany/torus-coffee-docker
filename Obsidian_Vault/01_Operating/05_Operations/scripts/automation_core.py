#!/usr/bin/env python3
"""
Torus Coffee Automation Core
Shared utilities for all automation scripts.
"""
import json
import time
import logging
import sys
from pathlib import Path
from datetime import datetime

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
AUTOMATION_DIR = VAULT / "10_Skills_Library" / "05_Operations"
LOGS_DIR = AUTOMATION_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"automation_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('torus_automation')


class AutomationError(Exception):
    """Base automation error."""
    pass


class CredentialError(AutomationError):
    """Missing or invalid credential."""
    pass


def load_json(filepath: Path) -> dict:
    """Load JSON config file safely."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return {}


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON config file safely."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved config: {filepath.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def retry(max_attempts=3, delay=2, backoff=2):
    """
    Decorator for retrying functions with exponential backoff.
    
    Usage:
        @retry(max_attempts=3, delay=2, backoff=2)
        def my_api_call():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            last_error = None
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}"
                    )
                    if attempt < max_attempts:
                        logger.info(f"Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    attempt += 1
            
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_error
        return wrapper
    return decorator


def get_credential(service: str, key: str = None) -> dict:
    """
    Load credentials for a service.
    
    Args:
        service: Service name (buffer, zapier, hubspot, trello)
        key: Optional specific key to return
    
    Returns:
        Credentials dict or specific value
    """
    creds_file = AUTOMATION_DIR / f"{service}_credentials.json"
    creds = load_json(creds_file)
    
    if not creds:
        raise CredentialError(f"No credentials found for {service}")
    
    if key:
        return creds.get(key)
    return creds


def validate_credentials():
    """Check all service credentials are present."""
    services = ['buffer', 'zapier', 'hubspot', 'trello']
    status = {}
    
    for service in services:
        try:
            creds = get_credential(service)
            status[service] = {
                'ok': True,
                'account': creds.get('account', creds.get('service', 'N/A')),
                'verified': creds.get('verified', False)
            }
        except CredentialError:
            status[service] = {'ok': False, 'error': 'Missing credentials'}
        except Exception as e:
            status[service] = {'ok': False, 'error': str(e)}
    
    return status


def print_status():
    """Print credential status."""
    status = validate_credentials()
    
    print("\n=== AUTOMATION CREDENTIAL STATUS ===\n")
    for service, info in status.items():
        if info['ok']:
            print(f"✅ {service.upper():12} {info.get('account', 'OK'):30} Verified: {info.get('verified')}")
        else:
            print(f"❌ {service.upper():12} {info.get('error', 'Unknown')}")
    print()


if __name__ == "__main__":
    print_status()
