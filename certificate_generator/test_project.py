import pytest
import os
from unittest.mock import patch
# IMPORTANT: This line assumes project.py is in the same directory
from project import Jar, check_deposit, generate_certificate, get_current_status

# --- Test 1: check_deposit (Logic fixed: only check, do not modify jar state) ---
def test_check_deposit():
    # Scenario 1: Empty Jar
    jar_empty = Jar(capacity=5)

    # Test 1.1: Valid deposit (should return True)
    assert check_deposit(jar_empty, 2) == True

    # Test 1.2: Deposit that exactly fills the jar (if jar was empty)
    assert check_deposit(jar_empty, 5) == True

    # Test 1.3: Deposit that exceeds capacity
    assert check_deposit(jar_empty, 6) == False

    # Scenario 2: Partially Full Jar (Size 2)
    jar_partial = Jar(capacity=5)
    jar_partial.deposit(2)

    # Test 2.1: Deposit that fills the rest (size 2, capacity 5, deposit 3)
    assert check_deposit(jar_partial, 3) == True

    # Test 2.2: Deposit that exceeds capacity (size 2, capacity 5, deposit 4)
    assert check_deposit(jar_partial, 4) == False

    # Test 2.3: Non-positive input (should raise ValueError)
    with pytest.raises(ValueError):
        check_deposit(jar_empty, -1)
    with pytest.raises(ValueError):
        check_deposit(jar_empty, 0)
    # Assuming check_deposit validates type
    with pytest.raises(ValueError):
        check_deposit(jar_empty, 1.5)


# --- Test 2: get_current_status ---
def test_get_current_status():
    jar = Jar(capacity=3)

    # Test 2.1: Empty jar status
    status_empty = get_current_status(jar)
    assert "Jar is empty" in status_empty
    assert "⚪" in status_empty

    # Test 2.2: Partial jar status
    jar.deposit(2)
    status_partial = get_current_status(jar)
    assert "2/3 cookies" in status_partial
    assert "🟡" in status_partial

    # Test 2.3: Full jar status
    jar.deposit(1)
    status_full = get_current_status(jar)
    assert "Jar is FULL" in status_full
    assert "🟢" in status_full


@patch('project.Canvas')
@patch('os.remove')
@patch('os.path.exists', return_value=True) # Mock exists to return True for cleanup check
def test_generate_certificate(mock_exists, mock_remove, MockCanvas):
    name = "Test User"
    cookies = 10
    expected_filename = "test_user_certificate.pdf"

    # Test 3.1: Function returns the correct filename
    filename = generate_certificate(name, cookies)
    assert filename == expected_filename

    # Test 3.2: Verify that the PDF creation was attempted
    # Check that the Canvas object was initialized and save() was called.
    MockCanvas.assert_called_once()
    MockCanvas.return_value.save.assert_called_once()

    # The cleanup logic in the original test is no longer needed here
    # as we mock the file interaction.
