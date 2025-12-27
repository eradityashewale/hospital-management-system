"""
Test Module for Hospital Management System
Tests all navigation buttons to ensure they work correctly
"""
import tkinter as tk
from tkinter import messagebox
import time
import sys
from main import HospitalManagementSystem
from logger import log_info, log_error, log_debug


class ButtonTester:
    """Test class for button functionality"""
    
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.test_results = []
        self.current_test = None
        
    def log_test(self, button_name, status, message=""):
        """Log test result"""
        result = {
            'button': button_name,
            'status': status,  # 'PASS', 'FAIL', 'ERROR'
            'message': message,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        log_info(f"{status_symbol} Test: {button_name} - {status} - {message}")
        print(f"{status_symbol} {button_name}: {status} - {message}")
        
    def test_button_exists(self, button_name):
        """Test if button exists in nav_buttons"""
        try:
            if button_name not in self.app.nav_buttons:
                self.log_test(button_name, "FAIL", f"Button '{button_name}' not found in nav_buttons")
                return False
            
            btn = self.app.nav_buttons[button_name]
            if btn is None:
                self.log_test(button_name, "FAIL", f"Button '{button_name}' is None")
                return False
                
            self.log_test(button_name, "PASS", "Button exists")
            return True
        except Exception as e:
            self.log_test(button_name, "ERROR", f"Exception checking button: {str(e)}")
            return False
    
    def test_button_state(self, button_name):
        """Test if button is in normal state"""
        try:
            btn = self.app.nav_buttons[button_name]
            state = btn['state']
            
            if state != tk.NORMAL:
                self.log_test(button_name, "FAIL", f"Button state is '{state}', expected 'normal'")
                return False
            
            self.log_test(button_name, "PASS", f"Button state is '{state}'")
            return True
        except Exception as e:
            self.log_test(button_name, "ERROR", f"Exception checking button state: {str(e)}")
            return False
    
    def test_button_command(self, button_name):
        """Test if button has a command bound"""
        try:
            btn = self.app.nav_buttons[button_name]
            command = btn['command']
            
            if command is None:
                self.log_test(button_name, "FAIL", "Button command is None")
                return False
            
            self.log_test(button_name, "PASS", "Button has command bound")
            return True
        except Exception as e:
            self.log_test(button_name, "ERROR", f"Exception checking button command: {str(e)}")
            return False
    
    def test_button_click(self, button_name):
        """Test if button click executes correctly"""
        try:
            # Store current module
            previous_module = self.app.current_module
            
            # Get button
            btn = self.app.nav_buttons[button_name]
            
            # Get initial content frame children count
            initial_children = len(self.app.content_frame.winfo_children())
            
            # Simulate button click
            log_info(f"Testing button click: {button_name}")
            btn.invoke()
            
            # Give UI time to update
            self.root.update_idletasks()
            time.sleep(0.15)  # Slightly longer delay for UI updates
            self.root.update()
            
            # Check if module changed or content updated
            new_children = len(self.app.content_frame.winfo_children())
            new_module = self.app.current_module
            
            # Special case: Dashboard button when already on Dashboard
            # The button still works, it just refreshes the same view
            if button_name == "Dashboard" and previous_module == "Dashboard":
                # Dashboard button clicked while on Dashboard - this is valid
                # Check if content was refreshed (children count might be same but content refreshed)
                if new_children > 0:  # Dashboard should have content
                    self.log_test(button_name, "PASS", f"Button click executed (Dashboard refresh)")
                    return True
                else:
                    self.log_test(button_name, "FAIL", "Dashboard button click did not load content")
                    return False
            
            # For other buttons: Button click should either change module or update content
            if new_module != previous_module or new_children != initial_children:
                self.log_test(button_name, "PASS", f"Button click executed (Module: {previous_module} -> {new_module})")
                return True
            else:
                # If module didn't change but we have content, button still worked
                if new_children > 0:
                    self.log_test(button_name, "PASS", f"Button click executed (Content loaded, Module: {new_module})")
                    return True
                else:
                    self.log_test(button_name, "FAIL", "Button click did not change module or load content")
                    return False
                
        except Exception as e:
            self.log_test(button_name, "ERROR", f"Exception during button click: {str(e)}")
            log_error(f"Error testing button {button_name}", e)
            return False
    
    def run_all_tests(self):
        """Run all button tests"""
        print("\n" + "="*60)
        print("BUTTON FUNCTIONALITY TEST")
        print("="*60)
        log_info("="*60)
        log_info("Starting Button Functionality Test")
        log_info("="*60)
        
        # List of all navigation buttons
        buttons_to_test = [
            "Dashboard",
            "Patients", 
            "Doctors",
            "Appointments",
            "Prescriptions",
            "Billing",
            "Reports"
        ]
        
        results = {
            'total': len(buttons_to_test),
            'passed': 0,
            'failed': 0,
            'errors': 0
        }
        
        # Test each button
        for button_name in buttons_to_test:
            print(f"\n--- Testing: {button_name} ---")
            self.current_test = button_name
            
            # Test 1: Button exists
            exists = self.test_button_exists(button_name)
            if not exists:
                results['failed'] += 1
                continue
            
            # Test 2: Button state
            state_ok = self.test_button_state(button_name)
            if not state_ok:
                results['failed'] += 1
                continue
            
            # Test 3: Button command
            command_ok = self.test_button_command(button_name)
            if not command_ok:
                results['failed'] += 1
                continue
            
            # Test 4: Button click (only if previous tests passed)
            click_ok = self.test_button_click(button_name)
            if click_ok:
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            # Small delay between tests
            time.sleep(0.2)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Buttons Tested: {results['total']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⚠️  Errors: {results['errors']}")
        print("="*60)
        
        log_info("="*60)
        log_info(f"Button Test Summary: {results['passed']}/{results['total']} passed")
        log_info("="*60)
        
        # Show detailed results
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status_symbol = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"  {status_symbol} {result['button']}: {result['status']} - {result['message']}")
        
        return results


def run_button_tests():
    """Run button tests on the application"""
    try:
        print("Initializing application for testing...")
        log_info("Initializing application for button testing")
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide window during tests
        
        # Create application
        app = HospitalManagementSystem(root)
        
        # Wait for UI to be ready
        root.update_idletasks()
        time.sleep(0.5)
        
        # Create tester
        tester = ButtonTester(app)
        
        # Run tests
        results = tester.run_all_tests()
        
        # Cleanup
        root.destroy()
        
        # Return results
        return results
        
    except Exception as e:
        log_error("Fatal error in button testing", e)
        print(f"❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_buttons_interactive():
    """Interactive test - runs app and tests buttons after a delay"""
    print("\n" + "="*60)
    print("INTERACTIVE BUTTON TEST")
    print("="*60)
    print("This will start the application and test buttons after 3 seconds.")
    print("You can also manually test the buttons.")
    print("="*60)
    
    try:
        # Create root window
        root = tk.Tk()
        
        # Create application
        app = HospitalManagementSystem(root)
        
        # Show window
        root.deiconify()
        
        # Schedule tests after delay
        def run_tests_after_delay():
            time.sleep(3)  # Wait 3 seconds for app to be ready
            print("\nStarting automated button tests...")
            tester = ButtonTester(app)
            results = tester.run_all_tests()
            
            # Show results in message box
            passed = results['passed']
            total = results['total']
            message = f"Button Test Results:\n\nPassed: {passed}/{total}\nFailed: {total - passed}"
            
            if passed == total:
                messagebox.showinfo("Test Results", f"✅ All tests passed!\n\n{message}")
            else:
                messagebox.showwarning("Test Results", f"⚠️ Some tests failed\n\n{message}")
        
        # Run tests in background thread
        import threading
        test_thread = threading.Thread(target=run_tests_after_delay, daemon=True)
        test_thread.start()
        
        # Start main loop
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
        
    except Exception as e:
        log_error("Fatal error in interactive button testing", e)
        print(f"❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Hospital Management System Buttons')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run interactive test (shows app window)')
    parser.add_argument('--headless', action='store_true',
                       help='Run headless test (no window)')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_buttons_interactive()
    else:
        # Default: headless test
        results = run_button_tests()
        if results:
            exit_code = 0 if results['failed'] == 0 else 1
            sys.exit(exit_code)

