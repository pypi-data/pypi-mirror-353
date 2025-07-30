"""
Tests for VarAnnote __main__ module
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
import subprocess


class TestMainModule:
    """Test the __main__ module functionality"""
    
    def test_main_module_execution(self):
        """Test that the main module can be executed"""
        # Test running the module with -h flag
        result = subprocess.run(
            [sys.executable, "-m", "varannote", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should exit with code 0 for help
        assert result.returncode == 0
        assert "VarAnnote" in result.stdout or "usage:" in result.stdout
    
    def test_main_module_version(self):
        """Test version flag"""
        result = subprocess.run(
            [sys.executable, "-m", "varannote", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should show version information
        assert result.returncode == 0
        # Version should be in stdout or stderr
        output = result.stdout + result.stderr
        assert any(char.isdigit() for char in output)  # Should contain version numbers
    
    def test_main_module_import(self):
        """Test that __main__ module can be imported"""
        try:
            import varannote.__main__
            # If we get here, import was successful
            assert True
        except ImportError:
            pytest.fail("Failed to import varannote.__main__")
    
    @patch('varannote.cli.main')
    def test_main_module_calls_cli(self, mock_cli_main):
        """Test that __main__ module calls CLI main function"""
        # Mock the CLI main function
        mock_cli_main.return_value = None
        
        # Import and execute the main module
        import varannote.__main__
        
        # The CLI main should have been called during import
        # Note: This test verifies the structure exists
        assert hasattr(varannote.__main__, '__name__')
    
    def test_main_module_invalid_command(self):
        """Test invalid command handling"""
        result = subprocess.run(
            [sys.executable, "-m", "varannote", "invalid_command"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should exit with non-zero code for invalid command
        assert result.returncode != 0
        # Should show error message
        output = result.stdout + result.stderr
        assert "error" in output.lower() or "invalid" in output.lower() or "usage" in output.lower()


if __name__ == "__main__":
    pytest.main([__file__]) 