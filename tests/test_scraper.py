import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import matches_criteria

def test_matches_criteria_empty_categories():
    assert matches_criteria("Some job post", []) == True

def test_matches_criteria_match_found():
    categories = ["python", "remote"]
    assert matches_criteria("Looking for a Python developer", categories) == True
    assert matches_criteria("Remote job available", categories) == True

def test_matches_criteria_no_match():
    categories = ["python", "remote"]
    assert matches_criteria("Looking for a Java developer onsite", categories) == False

def test_matches_criteria_case_insensitive():
    categories = ["PYTHON"]
    assert matches_criteria("Looking for a python dev", categories) == True
