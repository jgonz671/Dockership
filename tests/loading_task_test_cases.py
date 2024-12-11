
# Test cases for the loading task functionality

test_cases = [
    {
        "test_case_id": "TC001",
        "description": "Check behavior when no file is uploaded",
        "input": "None",
        "expected_output": "Error message: 'No file uploaded. Please upload a file first.'",
        "notes": "Verify that the error message displays correctly when no file is uploaded."
    },
    {
        "test_case_id": "TC002",
        "description": "Validate parsing of valid file content",
        "input": "File with valid grid data",
        "expected_output": "Parsed grid displayed successfully",
        "notes": "Ensure that the grid is parsed and displayed correctly for valid input."
    },
    {
        "test_case_id": "TC003",
        "description": "Validate parsing of invalid file content",
        "input": "File with malformed grid data",
        "expected_output": "Error message: 'Invalid file format'",
        "notes": "Check that an appropriate error message is shown for invalid input."
    },
    {
        "test_case_id": "TC004",
        "description": "Check move instructions for a valid move",
        "input": "Default moves in database",
        "expected_output": "Move instructions displayed for the first move",
        "notes": "Ensure that move instructions are correct and visible."
    },
    {
        "test_case_id": "TC005",
        "description": "Validate successful move confirmation",
        "input": "Click 'Confirm Move' button",
        "expected_output": "Move logged and next move displayed",
        "notes": "Check that the move is logged and the next move is updated."
    },
    {
        "test_case_id": "TC006",
        "description": "Test reset functionality after completing all moves",
        "input": "Click 'Start Over' button after all moves",
        "expected_output": "Current move index reset to 0",
        "notes": "Verify that the state resets properly for a new sequence."
    },
    {
        "test_case_id": "TC007",
        "description": "Check behavior when moves collection is empty",
        "input": "Empty database",
        "expected_output": "Default moves inserted and displayed",
        "notes": "Ensure default moves are correctly inserted if none exist."
    },
]

def get_test_cases():
    """Returns the list of test cases."""
    return test_cases
