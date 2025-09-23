import sys
import logging
import os
import time
import argparse
from typing import List, Dict, Any, Optional
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from module.envfacebook import perform_manual_login, parse_excel_test_data, initialize_driver, send_message_to_chatbot, get_chatbot_response, take_screenshot, generate_html_report, CHATBOT_ID

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

from session_manager import get_latest_session, validate_session_cookies, create_session_folder

def setup_test_environment() -> tuple[str, str]:
    """Set up the test environment and handle login."""
    logger.info("Setting up test environment...")
    
    try:
        # Check for existing valid session
        latest_session = get_latest_session()
        if latest_session:
            session_id, session_folder = latest_session
            cookie_file = os.path.join(session_folder, 'cookies.json')
            if validate_session_cookies(cookie_file):
                logger.info(f"Using existing valid session: {session_id} in {session_folder}")
                return session_folder, session_id
        
        # If no valid session, perform manual login
        session_folder, session_id = perform_manual_login()
        logger.info(f"New session established: {session_id} in {session_folder}")
        return session_folder, session_id
    except Exception as e:
        logger.error(f"Failed to establish session: {e}")
        raise

def load_test_data(file_path: str) -> List[Dict[str, str]]:
    """Load test cases from CSV file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        test_cases = parse_excel_test_data(file_path)
        logger.info(f"Loaded {len(test_cases)} test cases from {file_path}")
        return test_cases
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        raise

def run_test_case(driver, test_case: Dict[str, str], index: int, screenshots_dir: str) -> Dict[str, Any]:
    """Run a single test case and return results."""
    question = test_case["question"]
    expected_response = test_case["expected_response"]
    screenshot_path = os.path.join(screenshots_dir, f"test_case_{index + 1}.png")
    
    result = {
        "question": question,
        "expected_response": expected_response,
        "actual_response": None,
        "status": "Fail",
        "log": "",
        "screenshot": os.path.basename(screenshot_path)
    }
    
    logger.info(f"Running test case {index + 1}: {question[:50]}...")
    
    try:
        # Send message to chatbot
        if send_message_to_chatbot(driver, question):
            # Wait a moment for response
            time.sleep(2)
            actual_response = get_chatbot_response(driver)
            
            if actual_response:
                result["actual_response"] = actual_response
                # Check if expected response is contained in actual response
                if expected_response.lower() in actual_response.lower():
                    result["status"] = "Pass"
                    result["log"] = "Expected response found in chatbot reply"
                    logger.info(f"Test case {index + 1} PASSED")
                else:
                    result["log"] = f"Expected: '{expected_response}', Got: '{actual_response[:100]}...'"
                    logger.warning(f"Test case {index + 1} FAILED - Response mismatch")
            else:
                result["log"] = "No response received from chatbot"
                logger.warning(f"Test case {index + 1} FAILED - No response")
        else:
            result["log"] = "Failed to send message to chatbot"
            logger.error(f"Test case {index + 1} FAILED - Could not send message")
    
    except Exception as e:
        result["log"] = f"Error during test execution: {str(e)}"
        logger.error(f"Test case {index + 1} ERROR - {e}")
    
    finally:
        # Always take screenshot
        try:
            take_screenshot(driver, screenshot_path)
        except Exception as e:
            logger.warning(f"Failed to take screenshot for test case {index + 1}: {e}")
    
    return result

def create_session_only():
    """Only creates a new session or validates an existing one."""
    logger.info("Starting session creation/validation process...")
    try:
        session_folder, session_id = setup_test_environment()
        logger.info(f"Session process completed. Session ID: {session_id}, Path: {session_folder}")
    except Exception as e:
        logger.error(f"Session creation/validation failed: {e}")
        sys.exit(1)

def main():
    """Main entry point for the chatbot testing solution."""
    logger.info("Starting Facebook chatbot automation testing...")
    
    # Initialize variables
    session_folder: Optional[str] = None
    session_id: Optional[str] = None
    driver = None
    test_results: List[Dict[str, Any]] = []
    
    try:
        # 1. Set up session and login
        session_folder, session_id = setup_test_environment()
        
        # 2. Load test data
        test_data_file = os.path.join('assets', 'csv', 'test_questions.csv')
        test_cases = load_test_data(test_data_file)
        
        if not test_cases:
            logger.warning("No test cases found in the data file")
            return
        
        # 3. Initialize driver and navigate to chatbot
        screenshots_dir = os.path.join(session_folder, 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        logger.info("Initializing WebDriver...")
        driver = initialize_driver(session_folder)
        
        chatbot_url = f"https://www.facebook.com/messages/t/{CHATBOT_ID}"
        logger.info(f"Navigating to chatbot: {chatbot_url}")
        driver.get(chatbot_url)
        
        # Wait for page to load and verify URL
        WebDriverWait(driver, 20).until(EC.url_contains(f"facebook.com/messages/t/{CHATBOT_ID}"))
        logger.info("Successfully navigated to chatbot page.")
        time.sleep(3)
        
        # 4. Run test cases with optimized execution
        logger.info(f"Starting execution of {len(test_cases)} test cases...")
        total_tests = len(test_cases)
        passed_tests = 0
        
        for i, test_case in enumerate(test_cases):
            result = run_test_case(driver, test_case, i, screenshots_dir)
            test_results.append(result)
            if result["status"] == "Pass":
                passed_tests += 1
        
        # 5. Generate comprehensive report
        logger.info("Generating test report...")
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        final_report_path = generate_html_report(test_results, screenshots_dir, report_dir)
        logger.info(f"Test report generated: {final_report_path}")
        
        # Summary with success rate
        failed = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"Test execution completed!")
        logger.info(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {failed} ({success_rate:.1f}%)")
        
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during test execution: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
        
        logger.info("Facebook chatbot automation testing finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Chatbot Automation Script")
    parser.add_argument(
        "--create-session", 
        action="store_true", 
        help="Only create or validate a session, then exit."
    )
    args = parser.parse_args()

    if args.create_session:
        create_session_only()
    else:
        main()