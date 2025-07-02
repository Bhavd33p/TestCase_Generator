import re
from typing import Tuple, Optional
def clean_requirement_ids(req_matches: list[str]) -> list[str]:
    clean_ids = []
    for req_id in req_matches:
        match = re.match(r'REQ[_\-]?(\d{1,})$', req_id)
        if match:
            number = int(match.group(1))
            clean_ids.append(f"REQ{number:03}")
    return clean_ids

def get_last_ids(generated_text: str) -> Tuple[Optional[str], int, Optional[str], int]:
    tc_matches = re.findall(r'Test Case ID:\s*([A-Z]{2,}[_\-]?\d+)', generated_text, re.IGNORECASE)
    print("Test Case Matches found:", tc_matches)

    req_matches = re.findall(r'Requirement ID:\s*([A-Z]{2,}[_\-]?\d+)', generated_text, re.IGNORECASE)
    req_matches = clean_requirement_ids(req_matches)
    print("Cleaned Requirement ID Matches:", req_matches)


    tc_prefix, tc_number = (None, 0)
    if tc_matches:
        last_tc = tc_matches[-1]
        match = re.match(r'([A-Za-z0-9_]+?)[_\-]?(\d+)$', last_tc, re.IGNORECASE)
        if match:
            tc_prefix = match.group(1).upper()
            tc_number = int(match.group(2))
    
    req_prefix, req_number = (None, 0)
    if req_matches:
        last_req = req_matches[-1]
        match = re.match(r'([A-Za-z0-9_]+?)[_\-]?(\d+)$', last_req, re.IGNORECASE)
        if match:
            req_prefix = match.group(1).upper()
            req_number = int(match.group(2))
    
    return tc_prefix, tc_number, req_prefix, req_number
