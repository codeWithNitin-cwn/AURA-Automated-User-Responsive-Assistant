import unittest
import sys
import os

# Add tools/ and tools/services/ to sys.path for test visibility
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools', 'services')))

from security import is_path_safe, is_app_safe, is_input_safe, WORKSPACE_DIR

class TestSecurity(unittest.TestCase):
    def test_sandbox_path_validation(self):
        # Valid path inside workspace
        safe_path = os.path.join(WORKSPACE_DIR, 'test_file.txt')
        self.assertTrue(is_path_safe(safe_path))
        
        # Path attempting traversal escape using ..
        unsafe_path = os.path.join(WORKSPACE_DIR, '..', 'escape.txt')
        self.assertFalse(is_path_safe(unsafe_path))
        
        # Absolute system paths outside workspace
        self.assertFalse(is_path_safe("C:\\Windows\\System32\\cmd.exe"))
        self.assertFalse(is_path_safe("C:\\Users\\Public\\Downloads"))
        
    def test_app_whitelisting(self):
        # Whitelisted apps
        self.assertTrue(is_app_safe("chrome"))
        self.assertTrue(is_app_safe("vs code"))
        self.assertTrue(is_app_safe("notepad"))
        
        # Disallowed apps
        self.assertFalse(is_app_safe("regedit"))
        self.assertFalse(is_app_safe("powershell.exe"))
        self.assertFalse(is_app_safe("malicious_runner"))

    def test_input_sanitization(self):
        # Safe input commands
        self.assertTrue(is_input_safe("Show me my RAM usage"))
        self.assertTrue(is_input_safe("Create a notes file"))
        
        # Malicious blacklisted keyword patterns
        self.assertFalse(is_input_safe("rmdir /s /q workspace"))
        self.assertFalse(is_input_safe("format C:"))
        self.assertFalse(is_input_safe("reg delete HKCU"))

if __name__ == '__main__':
    unittest.main()

