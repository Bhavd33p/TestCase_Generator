import sys
import os
import pytest
import allure
import logging

# Add src to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from services.requirement_extractor import clean_text, extract_numbered_requirements

# Setup logger
logger = logging.getLogger(__name__)

@allure.title("Test clean_text function")
@allure.description("This test verifies that the clean_text function correctly removes unicode normalization.")
def test_clean_text():
    """
    Tests the clean_text function.
    """
    allure.step("Define input text with special characters")
    input_text = "Hēllō Wōrld"
    logger.info(f"Input text: {input_text}")

    allure.step("Define the expected cleaned text")
    expected_text = "Hello World"
    logger.info(f"Expected text: {expected_text}")

    allure.step("Call the clean_text function")
    actual_text = clean_text(input_text)
    logger.info(f"Actual text: {actual_text}")

    allure.step("Assert that the actual text matches the expected text")
    assert actual_text == expected_text

@allure.title("Test extract_numbered_requirements function")
@allure.description("This test verifies that extract_numbered_requirements correctly extracts numbered requirements from text.")
def test_extract_numbered_requirements():
    """
    Tests the extract_numbered_requirements function.
    """
    allure.step("Define input text with numbered requirements")
    text = "1. This is the first requirement.\n2. This is the second requirement.\nSome other text.\n3. This is the third."
    logger.info(f"Input text for requirement extraction:\n{text}")
    
    allure.step("Define the expected list of requirements")
    expected = [
        "This is the first requirement.",
        "This is the second requirement.",
        "This is the third."
    ]
    logger.info(f"Expected requirements: {expected}")
    
    allure.step("Call the extract_numbered_requirements function")
    actual = extract_numbered_requirements(text)
    logger.info(f"Actual requirements: {actual}")
    
    allure.step("Assert that the actual list matches the expected list")
    assert actual == expected

@allure.title("Test extract_numbered_requirements with no requirements")
@allure.description("This test verifies that extract_numbered_requirements returns an empty list for text with no numbered requirements.")
def test_extract_numbered_requirements_no_match():
    """
    Tests the extract_numbered_requirements function when no requirements are present.
    """
    allure.step("Define input text without numbered requirements")
    text = "There are no requirements here."
    logger.info(f"Input text with no requirements: {text}")
    
    allure.step("Call the extract_numbered_requirements function")
    actual = extract_numbered_requirements(text)
    logger.info(f"Actual result for no requirements: {actual}")
    
    allure.step("Assert that the result is an empty list")
    assert actual == [] 