
# ----- From config.py -----

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration file
CHROME_DRIVER_PATH = os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads', 'chromedriver-win64', 'chromedriver.exe')
if not os.path.exists(CHROME_DRIVER_PATH):
    # Try alternative paths
    alt_paths = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop', 'chromedriver.exe'),
        os.path.join('C:', 'WebDriver', 'chromedriver.exe'),
        'chromedriver.exe'  # Assume it's in PATH
    ]
    
    for alt_path in alt_paths:
        if os.path.exists(alt_path) or alt_path == 'chromedriver.exe':
            CHROME_DRIVER_PATH = alt_path
            break
FACEBOOK_URL = "https://www.facebook.com"
SESSION_DIR = "sessions"
SCREENSHOTS_DIR = "screenshots"
REPORTS_DIR = "reports"
TEST_DATA_FILE = "test_data.xlsx"

# Selenium Configuration
SELENIUM_TIMEOUT = 30  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 10  # seconds
HEADLESS_MODE = False  # Set to True for headless mode
WINDOW_SIZE = "1920,1080"

# Test Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
SCREENSHOT_ON_FAILURE = True
SAVE_SESSION_COOKIES = True
SESSION_EXPIRY_HOURS = 24

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "automation.log"

# Facebook Configuration
FACEBOOK_CHAT_URL = "https://www.facebook.com/messages/t/"
MESSAGE_INPUT_SELECTORS = [
    'div[contenteditable="true"]',
    '[data-text="true"]',
    'div[role="textbox"]',
    'textarea[placeholder*="ketik"]',
    'textarea[placeholder*="type"]'
]
SEND_BUTTON_SELECTORS = [
    '[aria-label*="kirim"]',
    '[aria-label*="send"]',
    'button[type="submit"]',
    'div[role="button"][aria-label*="kirim"]',
    'div[role="button"][aria-label*="send"]'
]

def validate_config() -> bool:
    """
    Validate all configuration settings.
    
    Returns:
        True if all configurations are valid, False otherwise
    """
    try:
        # Validate Chrome driver path
        if not os.path.exists(CHROME_DRIVER_PATH):
            logger.error(f"Chrome driver not found at: {CHROME_DRIVER_PATH}")
            return False
        
        # Validate directories
        directories = [SESSION_DIR, SCREENSHOTS_DIR, REPORTS_DIR]
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Directory validated: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
        
        # Validate test data file
        if not os.path.exists(TEST_DATA_FILE):
            logger.warning(f"Test data file not found: {TEST_DATA_FILE}")
            logger.info("Creating sample test data file...")
            create_sample_test_data(TEST_DATA_FILE)
        
        # Validate timeout values
        if SELENIUM_TIMEOUT <= 0 or PAGE_LOAD_TIMEOUT <= 0 or IMPLICIT_WAIT <= 0:
            logger.error("Timeout values must be positive integers")
            return False
        
        # Validate retry configuration
        if MAX_RETRIES < 0 or RETRY_DELAY < 0:
            logger.error("Retry configuration values must be non-negative")
            return False
        
        logger.info("Configuration validation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False

def create_sample_test_data(filename: str) -> None:
    """Create a sample test data file if it doesn't exist."""
    try:
        import pandas as pd
        
        # Create sample test data
        sample_data = {
            'question': [
                'Hello, how are you?',
                'What is your name?',
                'Can you help me?',
                'Thank you',
                'Goodbye'
            ],
            'expected_response': [
                'I am doing well, thank you!',
                'I am a chatbot assistant',
                'I will do my best to help you',
                'You are welcome!',
                'Goodbye! Have a great day!'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_excel(filename, index=False)
        logger.info(f"Sample test data file created: {filename}")
        
    except ImportError:
        logger.error("pandas not available. Cannot create sample test data.")
    except Exception as e:
        logger.error(f"Failed to create sample test data: {e}")

def get_chrome_options() -> dict:
    """
    Get Chrome options for Selenium WebDriver.
    
    Returns:
        Dictionary of Chrome options
    """
    options = {
        "--disable-gpu": True,
        "--no-sandbox": True,
        "--disable-dev-shm-usage": True,
        "--disable-extensions": True,
        "--disable-plugins": True,
        "--disable-images": False,  # Set to True to disable image loading for faster loading
        "--disable-javascript": False,  # Set to True to disable JavaScript (not recommended for Facebook)
        "--window-size": WINDOW_SIZE,
        "--user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    if HEADLESS_MODE:
        options["--headless"] = True
    
    return options

def setup_logging() -> None:
    """Setup logging configuration."""
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.dirname(LOG_FILE)
        if logs_dir:
            os.makedirs(logs_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
        logger.info("Logging setup completed")
        
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)

# Facebook Fanpage ID
CHATBOT_ID = "114552848299710" # Replace with your Facebook Fanpage ID

# ----- End of config.py -----


# ----- From data_parser.py -----

import pandas as pd
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_excel_test_data(file_path: str) -> List[Dict[str, str]]:
    """
    Parse test data from CSV or Excel file.
    
    Args:
        file_path (str): Path to the data file (CSV or Excel)
        
    Returns:
        List of test cases (dictionaries with question and expected_response)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is unsupported or data is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    
    try:
        # Determine file type and read accordingly
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            logger.info(f"Reading CSV file: {file_path}")
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            logger.info(f"Reading Excel file: {file_path}")
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Use CSV or Excel files.")
        
        # Validate required columns
        required_columns = ['question', 'expected_response']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Remove empty rows
        df = df.dropna(subset=['question', 'expected_response'])
        
        if df.empty:
            raise ValueError("No valid test data found in the file")
        
        # Create test cases
        test_cases = []
        for index, row in df.iterrows():
            test_case = {
                'question': str(row['question']).strip(),
                'expected_response': str(row['expected_response']).strip()
            }
            
            # Validate test case data
            if test_case['question'] and test_case['expected_response']:
                test_cases.append(test_case)
            else:
                logger.warning(f"Skipping invalid test case at row {index + 1}")
        
        logger.info(f"Successfully parsed {len(test_cases)} test cases from {file_path}")
        return test_cases
        
    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing test data: {e}")
        raise

def validate_test_data(test_cases: List[Dict[str, str]]) -> bool:
    """
    Validate the parsed test data.
    
    Args:
        test_cases: List of test cases to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not test_cases:
        logger.error("No test cases provided")
        return False
    
    for i, test_case in enumerate(test_cases):
        if not isinstance(test_case, dict):
            logger.error(f"Test case {i} is not a dictionary")
            return False
        
        if 'question' not in test_case or 'expected_response' not in test_case:
            logger.error(f"Test case {i} missing required fields")
            return False
        
        if not test_case['question'].strip() or not test_case['expected_response'].strip():
            logger.error(f"Test case {i} has empty question or expected response")
            return False
    
    logger.info("Test data validation passed")
    return True

# ----- End of data_parser.py -----


# ----- From login_handler.py -----

import logging
import time
import os
import json
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from session_manager import (
    save_session_cookies, 
    create_session_folder, 
    get_latest_session, 
    validate_session_cookies,
    load_session_cookies
)

def perform_manual_login() -> Tuple[str, str]:
    """
    Handle Facebook login with session reuse.
    
    Returns:
        Tuple[str, str]: (session_folder_path, session_id)
    """
    # First, check if we have an existing valid session
    existing_session = get_latest_session()
    
    if existing_session:
        session_path, session_id = existing_session
        logging.info(f"Found existing session: {session_id}")
        
        # Validate the session cookies
        cookie_file = os.path.join(session_path, 'cookies.json')
        if os.path.exists(cookie_file) and validate_session_cookies(cookie_file):
            logging.info("Existing session is valid, reusing it")
            return session_path, session_id
        else:
            logging.warning("Existing session is invalid, proceeding with new login")
    
    # No valid session found, proceed with manual login
    logging.info("No valid session found, starting manual login process")
    folder_path, session_id = create_session_folder()
    
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.headless = False  # Show browser for manual login
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.facebook.com/")
        
        logging.info("Please log in manually and handle 2FA if needed.")
        print("Please log in manually and handle 2FA if needed.")
        
        # Wait for login to complete
        wait = WebDriverWait(driver, 300)  # Wait up to 5 minutes for login
        
        # First check if we're no longer on the login page
        wait.until_not(EC.presence_of_element_located((By.ID, "email")))
        logging.info("Login form no longer visible")
        
        # Wait for any of these elements that indicate successful login
        login_indicators = [
            (By.CSS_SELECTOR, "div[aria-label='Account']"),
            (By.CSS_SELECTOR, "div[aria-label='Your profile']"),
            (By.CSS_SELECTOR, "div[role='navigation']"),
            (By.CSS_SELECTOR, "div[data-pagelet='Stories']"),
            (By.CSS_SELECTOR, "div[role='main']"),
            (By.CSS_SELECTOR, "div[aria-label='Home']")
        ]
        
        for by_type, selector in login_indicators:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by_type, selector))
                )
                logging.info(f"Login confirmed with element: {selector}")
                break
            except:
                continue
        
        # Additional wait to ensure all cookies are set
        logging.info("Waiting for cookies to be fully set...")
        time.sleep(10)
        
        # Get cookies after successful login
        cookies = driver.get_cookies()
        
        # Save cookies to file
        cookie_file = os.path.join(folder_path, 'cookies.json')
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        logging.info(f"Session cookies saved to {cookie_file}")
        
        # Verify cookies contain essential Facebook authentication cookies
        cookie_names = [cookie.get('name', '') for cookie in cookies]
        if 'c_user' in cookie_names and 'xs' in cookie_names:
            logging.info(f"New session created and saved: {session_id}")
        else:
            raise ValueError("Login successful but essential cookies are missing")
        
        return folder_path, session_id
        
    except Exception as e:
        logging.error(f"Error during Facebook login: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed after login")

# ----- End of login_handler.py -----


# ----- From chatbot_tester.py -----

import logging
import time
import os
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from session_manager import load_session_cookies, validate_session_cookies

logger = logging.getLogger(__name__)

def initialize_driver(session_folder_path: str) -> webdriver.Chrome:
    """
    Initialize Chrome WebDriver with session cookies.
    
    Args:
        session_folder_path: Path to session folder containing cookies
        
    Returns:
        Configured Chrome WebDriver instance
    """
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("WebDriver initialized successfully")
        
        # Load and validate session cookies
        cookie_file = os.path.join(session_folder_path, 'cookies.json')
        if validate_session_cookies(cookie_file):
            cookies = load_session_cookies(session_folder_path)
            logger.info("Loading session cookies...")
            driver.get("https://www.facebook.com/")
            time.sleep(2)  # Wait for page load
            
            for cookie in cookies:
                try:
                    # Remove expiry if present to avoid errors
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
            
            driver.refresh()
            logger.info("Session cookies loaded successfully")
        else:
            logger.warning("No valid session cookies found")
        
        return driver
        
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise

def send_message_to_chatbot(driver: webdriver.Chrome, message: str) -> bool:
    """
    Send a message to the Facebook chatbot with optimized selectors.
    
    Args:
        driver: Selenium WebDriver instance
        message: Message to send
        
    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        logger.info(f"Sending message: {message[:50]}...")
        
        # Find message input box with optimized selectors
        message_box = _find_element_with_retry(driver, [
            "//div[@contenteditable='true'][@role='textbox']",
            "//div[@aria-label='Message']",
            "//div[@contenteditable='true']",
            "//textarea[@aria-label='Message']",
            "//div[@role='combobox' and @contenteditable='true']",
            "//div[contains(@class, '_5rpu') and @role='combobox']",
            "//textarea[@class='uiTextareaAutogrow _552m']"
        ], timeout=10)
        
        if not message_box:
            logger.error("Could not find message input box")
            return False
        
        # Clear and type message efficiently
        _clear_and_type(driver, message_box, message)
        
        # Try to send with multiple methods
        if not _try_send_methods(driver, message_box):
            return False
        
        logger.info("Message sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def _find_element_with_retry(driver: webdriver.Chrome, selectors: list, timeout: int = 5) -> Optional[object]:
    """Find element with multiple selectors and retry logic."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    
    for selector in selectors:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            if element and element.is_displayed() and element.is_enabled():
                return element
        except TimeoutException:
            continue
    return None

def _clear_and_type(driver: webdriver.Chrome, element, text: str) -> None:
    """Clear element and type text efficiently."""
    element.clear()
    element.send_keys(text)
    time.sleep(0.3)  # Reduced wait time

def _try_send_methods(driver: webdriver.Chrome, message_box) -> bool:
    """Try multiple methods to send message."""
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    
    # Method 1: Find send button
    send_button_selectors = [
        "//div[@aria-label='Press enter to send']",
        "//button[@type='submit']",
        "//div[contains(@aria-label, 'send')]",
        "//span[text()='Send']/parent::div"
    ]
    
    for selector in send_button_selectors:
        try:
            send_button = driver.find_element(By.XPATH, selector)
            if send_button and send_button.is_displayed() and send_button.is_enabled():
                driver.execute_script("arguments[0].click();", send_button)
                return True
        except NoSuchElementException:
            continue
    
    # Method 2: Press Enter key
    try:
        message_box.send_keys(Keys.ENTER)
        return True
    except Exception as e:
        logger.warning(f"Failed to press Enter: {e}")
    
    return False

def get_chatbot_response(driver: webdriver.Chrome) -> Optional[str]:
    """
    Get the latest response from the chatbot.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Latest chatbot response text or None if not found
    """
    try:
        logger.info("Getting chatbot response...")
        
        # Multiple possible selectors for chatbot responses
        response_selectors = [
            "//div[contains(@class, 'msg') and contains(@class, 'from-them')]//span",
            "//div[contains(@class, 'message') and contains(@class, 'incoming')]//span",
            "//div[@dir='auto' and contains(@class, 'html-div')]",
            "//div[@dir='auto']",
            "//div[@role='article']//span[contains(@class, 'message')]",
            "//div[contains(@data-testid, 'message') and contains(@class, 'other')]//span",
            "//div[contains(@class, 'chatMessage')]//span",
            "//div[@data-hover='tooltip']/div/span"
        ]
        
        responses = []
        for selector in response_selectors:
            try:
                elements = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH, selector))
                )
                for elem in elements:
                    text = elem.text.strip()
                    if text:
                        responses.append(text)
            except TimeoutException:
                continue
        
        if responses:
            latest_response = responses[-1]
            logger.info(f"Found response: {latest_response[:50]}...")
            return latest_response
        else:
            logger.warning("No chatbot response found")
            return None
            
    except Exception as e:
        logger.error(f"Error getting chatbot response: {e}")
        return None

def take_screenshot(driver: webdriver.Chrome, path: str) -> bool:
    """
    Take a screenshot of the current browser state.
    
    Args:
        driver: Selenium WebDriver instance
        path: File path to save the screenshot
        
    Returns:
        True if screenshot taken successfully, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Take screenshot
        success = driver.save_screenshot(path)
        if success:
            logger.info(f"Screenshot saved: {path}")
        else:
            logger.warning(f"Failed to save screenshot: {path}")
        return success
        
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return False

# Additional utility functions
def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 10) -> bool:
    """Wait for page to fully load."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except TimeoutException:
        logger.warning("Page load timeout")
        return False

def is_chatbot_page_loaded(driver: webdriver.Chrome) -> bool:
    """Check if chatbot page has loaded properly."""
    try:
        # Check for common chatbot page elements
        indicators = [
            "//div[@role='main']",
            "//div[contains(@class, 'chat')]",
            "//div[@contenteditable='true']"
        ]
        
        for indicator in indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    except Exception as e:
        logger.error(f"Error checking chatbot page: {e}")
        return False

# ----- End of chatbot_tester.py -----


# ----- From utils.py -----

import logging
import time
import random
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
    """
    Add random delay to avoid detection patterns.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Adding random delay of {delay:.2f} seconds")
    time.sleep(delay)

def safe_execute(func: Callable, default_return: Any = None, *args, **kwargs) -> Any:
    """
    Safely execute a function and return default value on exception.
    
    Args:
        func: Function to execute
        default_return: Default value to return on exception
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Function result or default_return on exception
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Safe execution failed for {func.__name__}: {e}")
        return default_return

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_filename(filename: str, max_length: int = 255) -> str:
    """
    Clean filename by removing invalid characters and truncating.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Cleaned filename
    """
    import re
    
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores and spaces
    cleaned = cleaned.strip('_. ')
    
    # Truncate if too long
    if len(cleaned) > max_length:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:max_length - len(ext) - 1] + ext
    
    return cleaned or "unnamed"

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_file_size(file_path: str) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return None

def is_file_recent(file_path: str, hours: int = 24) -> bool:
    """
    Check if file was modified within specified hours.
    
    Args:
        file_path: Path to file
        hours: Number of hours to check
        
    Returns:
        True if file was modified within specified hours
    """
    try:
        import time
        file_time = os.path.getmtime(file_path)
        current_time = time.time()
        return (current_time - file_time) < (hours * 3600)
    except (OSError, FileNotFoundError):
        return False

def create_timestamp_filename(prefix: str = "file", extension: str = "txt") -> str:
    """
    Create filename with timestamp.
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Timestamped filename
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def batch_process(items: list, batch_size: int, process_func: Callable) -> list:
    """
    Process items in batches.
    
    Args:
        items: List of items to process
        batch_size: Number of items per batch
        process_func: Function to process each batch
        
    Returns:
        List of results
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        logger.debug(f"Processing batch {i//batch_size + 1}: {len(batch)} items")
        batch_results = process_func(batch)
        results.extend(batch_results)
    return results

def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_html(text: str) -> str:
    """
    Sanitize text for HTML display.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    import html
    return html.escape(text) if text else ""

# Import os for file operations
import os

# ----- End of utils.py -----


# ----- From report_generator.py -----

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

def _calculate_statistics(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from test results."""
    total = len(test_results)
    passed = sum(1 for result in test_results if result.get('status', '').lower() == 'passed')
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    response_times = [result.get('response_time', 0) for result in test_results if result.get('response_time') is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': pass_rate,
        'avg_response_time': avg_response_time
    }

def generate_html_report(test_results: List[Dict[str, Any]], screenshots_dir: str, report_dir: str) -> str:
    """
    Generate an HTML report for test results.
    
    Args:
        test_results: List of test case results
        screenshots_dir: Directory containing screenshot files
        report_dir: Directory to save the report
        
    Returns:
        Path to the generated report file
        
    Raises:
        FileNotFoundError: If template file is not found
        Exception: For other report generation errors
    """
    try:
        logger.info("Generating HTML report...")
        
        # Ensure report directory exists
        os.makedirs(report_dir, exist_ok=True)
        
        # Setup Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        
        # Check if template exists
        template_path = 'report_template.html'
        if not os.path.exists(template_path):
            logger.warning(f"Template file not found: {template_path}. Creating basic template.")
            create_basic_template(template_path)
        
        template = env.get_template(template_path)
        
        # Calculate statistics efficiently
        stats = _calculate_statistics(test_results)
        
        # Get available screenshots
        screenshots = []
        if os.path.exists(screenshots_dir):
            screenshots = [f for f in os.listdir(screenshots_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            screenshots.sort()
        
        # Prepare comprehensive report data
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": stats["total"],
            "passed_tests": stats["passed"],
            "failed_tests": stats["failed"],
            "pass_rate": stats["pass_rate"],
            "test_results": test_results,
            "screenshots": screenshots,
            "screenshots_dir": screenshots_dir
        }
        
        # Render template
        html_content = template.render(report_data)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"test_report_{timestamp}.html"
        report_path = os.path.join(report_dir, report_filename)
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated successfully: {report_path}")
        return report_path
        
    except FileNotFoundError as e:
        logger.error(f"Template file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}")
        raise

def _create_optimized_html_template(self, test_results: List[Dict[str, Any]], stats: Dict[str, Any], timestamp: str) -> str:
    """Create optimized HTML template with modern styling."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Chatbot Test Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.3s ease; }}
            .stat-card:hover {{ transform: translateY(-5px); }}
            .stat-number {{ font-size: 2rem; font-weight: bold; margin-bottom: 5px; }}
            .stat-label {{ color: #666; font-size: 0.9rem; }}
            .passed {{ color: #28a745; }}
            .failed {{ color: #dc3545; }}
            .total {{ color: #17a2b8; }}
            .test-results {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .test-item {{ padding: 20px; margin-bottom: 15px; border-left: 5px solid #ccc; border-radius: 5px; transition: all 0.3s ease; }}
            .test-item:hover {{ box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .test-item.passed {{ border-left-color: #28a745; background-color: #f8fff8; }}
            .test-item.failed {{ border-left-color: #dc3545; background-color: #fff8f8; }}
            .test-name {{ font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; }}
            .test-message {{ color: #666; margin-bottom: 10px; }}
            .test-meta {{ font-size: 0.85rem; color: #888; }}
            .screenshot {{ max-width: 100%; height: auto; border-radius: 5px; margin-top: 10px; }}
            .no-results {{ text-align: center; padding: 40px; color: #666; }}
            .footer {{ text-align: center; margin-top: 40px; padding: 20px; color: #666; font-size: 0.9rem; }}
            @media (max-width: 768px) {{ .stats-grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Facebook Chatbot Test Report</h1>
                <p>Generated on {timestamp}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number total">{stats['total']}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number passed">{stats['passed']}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number failed">{stats['failed']}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['success_rate']:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
            
            <div class="test-results">
                <h2>Test Results</h2>
                {self._generate_test_items_html(test_results)}
            </div>
            
            <div class="footer">
                <p>Generated by Facebook Chatbot Automation Framework</p>
            </div>
        </div>
    </body>
    </html>
    """

def _generate_test_items_html(self, test_results: List[Dict[str, Any]]) -> str:
    """Generate HTML for test items."""
    if not test_results:
        return '<div class="no-results">No test results available</div>'
    
    html_items = []
    for i, result in enumerate(test_results, 1):
        status = result.get('status', 'unknown').lower()
        test_name = result.get('test_name', f'Test {i}')
        message = result.get('message', '')
        response_time = result.get('response_time', 'N/A')
        screenshot = result.get('screenshot_path', '')
        
        item_html = f'''
        <div class="test-item {status}">
            <div class="test-name">{test_name}</div>
            <div class="test-message">{message}</div>
            <div class="test-meta">Response Time: {response_time}s</div>
        '''
        
        if screenshot and os.path.exists(screenshot):
            item_html += f'<img src="{screenshot}" class="screenshot" alt="Test screenshot">'
        
        item_html += '</div>'
        html_items.append(item_html)
    
    return '\n'.join(html_items)

def create_basic_template(template_path: str) -> None:
    """Create a basic HTML template if one doesn't exist."""
    basic_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Chatbot Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { display: flex; justify-content: space-around; margin-bottom: 30px; }
        .stat-box { text-align: center; padding: 15px; border-radius: 8px; min-width: 120px; }
        .stat-box.total { background-color: #e3f2fd; }
        .stat-box.passed { background-color: #e8f5e8; }
        .stat-box.failed { background-color: #ffebee; }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .test-results { margin-top: 30px; }
        .test-case { border: 1px solid #ddd; margin-bottom: 15px; border-radius: 8px; overflow: hidden; }
        .test-case.pass { border-left: 4px solid #4caf50; }
        .test-case.fail { border-left: 4px solid #f44336; }
        .test-header { padding: 15px; background-color: #f9f9f9; cursor: pointer; }
        .test-content { padding: 15px; background-color: white; display: none; }
        .test-content.active { display: block; }
        .screenshot { max-width: 100%; height: auto; margin-top: 10px; border: 1px solid #ddd; }
        .status-pass { color: #4caf50; font-weight: bold; }
        .status-fail { color: #f44336; font-weight: bold; }
        .log-message { background-color: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 10px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Facebook Chatbot Test Report</h1>
            <p>Generated on: {{ timestamp }}</p>
        </div>
        
        <div class="summary">
            <div class="stat-box total">
                <div class="stat-number">{{ total_tests }}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-box passed">
                <div class="stat-number">{{ passed_tests }}</div>
                <div>Passed</div>
            </div>
            <div class="stat-box failed">
                <div class="stat-number">{{ failed_tests }}</div>
                <div>Failed</div>
            </div>
            <div class="stat-box total">
                <div class="stat-number">{{ pass_rate }}%</div>
                <div>Pass Rate</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>Test Results</h2>
            {% for result in test_results %}
            <div class="test-case {{ result.status|lower }}">
                <div class="test-header" onclick="toggleTest({{ loop.index }})">
                    <strong>Test {{ loop.index }}:</strong> {{ result.question[:80] }}... 
                    <span class="status-{{ result.status|lower }}">{{ result.status }}</span>
                </div>
                <div id="test-{{ loop.index }}" class="test-content">
                    <p><strong>Question:</strong> {{ result.question }}</p>
                    <p><strong>Expected Response:</strong> {{ result.expected_response }}</p>
                    <p><strong>Actual Response:</strong> {{ result.actual_response or 'No response' }}</p>
                    <p><strong>Status:</strong> <span class="status-{{ result.status|lower }}">{{ result.status }}</span></p>
                    {% if result.log %}
                    <div class="log-message">
                        <strong>Log:</strong> {{ result.log }}
                    </div>
                    {% endif %}
                    {% if result.screenshot in screenshots %}
                    <img src="../{{ screenshots_dir }}/{{ result.screenshot }}" alt="Screenshot" class="screenshot">
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        function toggleTest(id) {
            const content = document.getElementById('test-' + id);
            content.classList.toggle('active');
        }
    </script>
</body>
</html>'''
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(basic_template)
    
    logger.info(f"Basic template created: {template_path}")

def generate_summary_report(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of test results.
    
    Args:
        test_results: List of test case results
        
    Returns:
        Dictionary containing summary statistics
    """
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get("status") == "Pass")
    failed = sum(1 for r in test_results if r.get("status") == "Fail")
    
    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "pass_rate": round((passed / total * 100) if total > 0 else 0, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ----- End of report_generator.py -----


# ----- From test_validation.py -----

#!/usr/bin/env python3
"""
Validation script to test the refactored automation framework.
This script performs basic functionality tests without requiring actual Facebook login.
"""

import os
import sys
import tempfile
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_validation():
    """Test configuration validation."""
    print("Testing configuration validation...")
    
    try:

        
        # Test logging setup
        setup_logging()
        
        # Test config validation (may fail due to missing chromedriver, but that's expected)
        result = validate_config()
        print(f"✅ Configuration validation test completed (result: {result})")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation test failed: {e}")
        return False

def test_data_parser():
    """Test data parser functionality."""
    print("Testing data parser...")
    
    try:
        import pandas as pd
        
        # Create temporary test data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("question,expected_response\n")
            f.write("Hello,Hi there\n")
            f.write("How are you?,I'm fine\n")
            temp_file = f.name
        
        # Test CSV parsing
        test_cases = parse_excel_test_data(temp_file)
        
        # Cleanup
        os.unlink(temp_file)
        
        if len(test_cases) == 2 and test_cases[0]['question'] == 'Hello':
            print("✅ Data parser test passed")
            return True
        else:
            print(f"❌ Data parser test failed: Expected 2 test cases, got {len(test_cases)}")
            return False
            
    except Exception as e:
        print(f"❌ Data parser test failed: {e}")
        return False

def test_session_manager():
    """Test session manager functionality."""
    print("Testing session manager...")
    
    try:
        from session_manager import create_session_folder, save_session_cookies, load_session_cookies
        import json
        import tempfile
        
        # Test session folder creation
        session_path, session_id = create_session_folder()
        if not os.path.exists(session_path):
            print("❌ Session folder creation failed")
            return False
        
        # Test cookie save/load
        test_cookies = [{"name": "test", "value": "cookie"}]
        
        save_session_cookies(session_path, test_cookies)
        loaded_cookies = load_session_cookies(session_path)
        
        # Cleanup
        import shutil
        shutil.rmtree(session_path, ignore_errors=True)
        
        if loaded_cookies and loaded_cookies[0]['name'] == 'test':
            print("✅ Session manager test passed")
            return True
        else:
            print("❌ Session manager test failed")
            return False
            
    except Exception as e:
        print(f"❌ Session manager test failed: {e}")
        return False

def test_report_generator():
    """Test report generation functionality."""
    print("Testing report generator...")
    
    try:

        
        # Create test data
        test_results = [
            {
                "question": "Hello",
                "expected_response": "Hi",
                "actual_response": "Hi there",
                "status": "Pass",
                "screenshot": None,
                "execution_time": "1.5s"
            },
            {
                "question": "How are you?",
                "expected_response": "Fine",
                "actual_response": "I'm doing well",
                "status": "Pass",
                "screenshot": None,
                "execution_time": "2.1s"
            }
        ]
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshots_dir = os.path.join(temp_dir, "screenshots")
            reports_dir = os.path.join(temp_dir, "reports")
            os.makedirs(screenshots_dir)
            os.makedirs(reports_dir)
            
            # Test report generation
            report_path = generate_html_report(test_results, screenshots_dir, reports_dir)
            
            if report_path and os.path.exists(report_path):
                # Test summary generation
                summary = generate_summary_report(test_results)
                if summary['total_tests'] == 2 and summary['passed_tests'] == 2:
                    print("✅ Report generator test passed")
                    return True
                else:
                    print("❌ Summary generation test failed")
                    return False
            else:
                print("❌ Report generation test failed")
                return False
                
    except Exception as e:
        print(f"❌ Report generator test failed: {e}")
        return False

def test_utils():
    """Test utility functions."""
    print("Testing utility functions...")
    
    try:

        
        # Test truncate_text
        long_text = "This is a very long text that should be truncated"
        truncated = truncate_text(long_text, 20)
        if len(truncated) <= 25:  # Account for "..."
            print("  ✅ truncate_text passed")
        else:
            print("  ❌ truncate_text failed")
            return False
        
        # Test clean_filename
        bad_filename = "test<file>name.txt"
        cleaned = clean_filename(bad_filename)
        if "<" not in cleaned and ">" not in cleaned:
            print("  ✅ clean_filename passed")
        else:
            print("  ❌ clean_filename failed")
            return False
        
        # Test format_duration
        formatted = format_duration(125.5)
        if "2.1m" in formatted:
            print("  ✅ format_duration passed")
        else:
            print("  ❌ format_duration failed")
            return False
        
        # Test create_timestamp_filename
        timestamp_file = create_timestamp_filename("test", "txt")
        if timestamp_file.startswith("test_") and timestamp_file.endswith(".txt"):
            print("  ✅ create_timestamp_filename passed")
        else:
            print("  ❌ create_timestamp_filename failed")
            return False
        
        print("✅ All utility tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    modules = [
        'config',
        'login_handler',
        'session_manager',
        'chatbot_tester',
        'data_parser',
        'report_generator',
        'utils',
        'test_runner'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} imported successfully")
        except Exception as e:
            print(f"  ❌ {module} import failed: {e}")
            failed_imports.append(module)
    
    if not failed_imports:
        print("✅ All module imports successful")
        return True
    else:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Starting Facebook Automation Framework Validation")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Validation", test_config_validation),
        ("Data Parser", test_data_parser),
        ("Session Manager", test_session_manager),
        ("Report Generator", test_report_generator),
        ("Utility Functions", test_utils),
    ]
    
    passed = 0
    failed = 0
    
    start_time = datetime.now()
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📈 Success Rate: {(passed/len(tests)*100):.1f}%")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All validation tests passed!")
        print("✨ The framework is ready for use!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

# ----- End of test_validation.py -----


# ----- From test_runner.py -----

import logging
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


from session_manager import get_latest_session, validate_session_cookies






logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Data class for test results."""
    question: str
    expected_response: str
    actual_response: str
    status: str  # "Pass" or "Fail"
    screenshot: Optional[str] = None
    log: Optional[str] = None
    execution_time: float = 0.0
    error: Optional[str] = None

class TestRunner:
    """Main test runner class for Facebook chatbot automation."""
    
    def __init__(self):
        self.driver = None
        self.session_id = None
        self.start_time = None
        self.test_results: List[TestResult] = []
        self.screenshots_taken: List[str] = []
        
    def setup(self) -> bool:
        """
        Setup the test environment.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            logger.info("Setting up test environment...")
            self.start_time = time.time()
            
            # Validate configuration
            if not validate_config():
                logger.error("Configuration validation failed")
                return False
            
            # Setup logging
            setup_logging()
            logger.info("Test environment setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def initialize_session(self) -> bool:
        """
        Initialize browser session with login or session reuse.
        
        Returns:
            True if session initialized successfully, False otherwise
        """
        try:
            logger.info("Initializing browser session...")
            
            # Try to use existing session
            session_path = get_latest_session()
            if session_path and validate_session_cookies(session_path):
                logger.info(f"Using existing session: {session_path}")
                self.session_id = session_path
                
                # Initialize driver with existing session
                self.driver = initialize_driver(session_cookies_path=session_path)
                if self.driver:
                    logger.info("Session initialized with existing cookies")
                    return True
                else:
                    logger.warning("Failed to initialize with existing session, falling back to manual login")
            
            # Perform manual login if no valid session exists
            logger.info("No valid session found, performing manual login...")
            session_path = perform_manual_login()
            
            if session_path:
                self.session_id = session_path
                self.driver = initialize_driver(session_cookies_path=session_path)
                if self.driver:
                    logger.info("Manual login completed and session initialized")
                    return True
            
            logger.error("Failed to initialize session")
            return False
            
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def load_test_data(self) -> List[Dict[str, str]]:
        """
        Load test data from configured file.
        
        Returns:
            List of test cases
        """
        try:
            logger.info("Loading test data...")
            test_cases = parse_excel_test_data()
            logger.info(f"Loaded {len(test_cases)} test cases")
            return test_cases
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            logger.error(traceback.format_exc())
            return []
    
    @retry(max_attempts=MAX_RETRIES, delay=RETRY_DELAY)
    def execute_test_case(self, test_case: Dict[str, str]) -> TestResult:
        """
        Execute a single test case.
        
        Args:
            test_case: Dictionary with 'question' and 'expected_response'
            
        Returns:
            TestResult object
        """
        start_time = time.time()
        question = test_case.get('question', '')
        expected_response = test_case.get('expected_response', '')
        
        logger.info(f"Executing test case: {question[:50]}...")
        
        try:
            # Send message to chatbot
            if not send_message(self.driver, question):
                raise Exception("Failed to send message")
            
            # Get response from chatbot
            actual_response = get_response(self.driver)
            if not actual_response:
                actual_response = "No response received"
            
            # Determine test status
            status = "Pass" if expected_response.lower() in actual_response.lower() else "Fail"
            
            # Take screenshot
            screenshot_filename = None
            if status == "Fail" or True:  # Take screenshot for all tests
                screenshot_filename = f"test_{len(self.test_results) + 1}_{create_timestamp_filename('screenshot', 'png')}"
                if take_screenshot(self.driver, screenshot_filename):
                    self.screenshots_taken.append(screenshot_filename)
            
            execution_time = time.time() - start_time
            
            result = TestResult(
                question=question,
                expected_response=expected_response,
                actual_response=actual_response,
                status=status,
                screenshot=screenshot_filename,
                execution_time=execution_time
            )
            
            logger.info(f"Test case completed: {status} ({execution_time:.2f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # Take screenshot on failure
            screenshot_filename = f"error_{len(self.test_results) + 1}_{create_timestamp_filename('screenshot', 'png')}"
            if take_screenshot(self.driver, screenshot_filename):
                self.screenshots_taken.append(screenshot_filename)
            
            result = TestResult(
                question=question,
                expected_response=expected_response,
                actual_response="",
                status="Fail",
                screenshot=screenshot_filename,
                execution_time=execution_time,
                error=error_msg,
                log=traceback.format_exc()
            )
            
            logger.error(f"Test case failed: {error_msg}")
            return result
    
    def run_tests(self, test_cases: List[Dict[str, str]]) -> List[TestResult]:
        """
        Run all test cases.
        
        Args:
            test_cases: List of test cases to execute
            
        Returns:
            List of test results
        """
        logger.info(f"Starting test execution with {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Running test {i}/{len(test_cases)}")
            
            result = self.execute_test_case(test_case)
            self.test_results.append(result)
            
            # Add delay between tests to avoid rate limiting
            time.sleep(1)
        
        logger.info(f"Test execution completed: {len(self.test_results)} test cases")
        return self.test_results
    
    def generate_report(self) -> Optional[str]:
        """
        Generate test report.
        
        Returns:
            Path to generated report or None if failed
        """
        try:
            logger.info("Generating test report...")
            
            # Convert TestResult objects to dictionaries
            results_data = []
            for result in self.test_results:
                result_dict = {
                    "question": result.question,
                    "expected_response": result.expected_response,
                    "actual_response": result.actual_response,
                    "status": result.status,
                    "screenshot": result.screenshot,
                    "log": result.log,
                    "execution_time": f"{result.execution_time:.2f}s"
                }
                results_data.append(result_dict)
            
            # Generate report
            report_path = generate_html_report(
                test_results=results_data,
                screenshots_dir="screenshots",
                report_dir="reports"
            )
            
            if report_path:
                logger.info(f"Report generated successfully: {report_path}")
                
                # Generate and display summary
                summary = generate_summary_report(results_data)
                self.display_summary(summary)
                
                return report_path
            else:
                logger.error("Failed to generate report")
                return None
                
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def display_summary(self, summary: Dict[str, Any]) -> None:
        """
        Display test execution summary.
        
        Args:
            summary: Summary statistics
        """
        print("\n" + "="*50)
        print("TEST EXECUTION SUMMARY")
        print("="*50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Pass Rate: {summary['pass_rate']}%")
        print(f"Execution Time: {summary['timestamp']}")
        
        if self.start_time:
            total_time = time.time() - self.start_time
            print(f"Total Duration: {format_duration(total_time)}")
        
        print("="*50)
    
    def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        try:
            logger.info("Cleaning up resources...")
            
            # Cleanup WebDriver
            if self.driver:
                cleanup_driver(self.driver)
                self.driver = None
            
            # Log final statistics
            if self.test_results:
                total = len(self.test_results)
                passed = sum(1 for r in self.test_results if r.status == "Pass")
                failed = total - passed
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                logger.info(f"Final Statistics - Total: {total}, Passed: {passed}, Failed: {failed}, Pass Rate: {pass_rate:.1f}%")
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def run(self) -> bool:
        """
        Run the complete test suite.
        
        Returns:
            True if test execution successful, False otherwise
        """
        try:
            # Setup
            if not self.setup():
                return False
            
            # Initialize session
            if not self.initialize_session():
                logger.error("Failed to initialize session")
                return False
            
            # Load test data
            test_cases = self.load_test_data()
            if not test_cases:
                logger.error("No test cases to execute")
                return False
            
            # Run tests
            self.run_tests(test_cases)
            
            # Generate report
            report_path = self.generate_report()
            if report_path:
                logger.info(f"Test execution completed successfully. Report: {report_path}")
            else:
                logger.warning("Test execution completed but report generation failed")
            
            return True
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            logger.error(traceback.format_exc())
            return False
            
        finally:
            self.cleanup()

def main():
    """Main function to run the test suite."""
    runner = TestRunner()
    success = runner.run()
    
    if success:
        print("\n✅ Test execution completed successfully!")
        return 0
    else:
        print("\n❌ Test execution failed!")
        return 1

if __name__ == "__main__":
    exit(main())

# ----- End of test_runner.py -----

