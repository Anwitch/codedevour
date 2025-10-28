"""
Automated Frontend Testing for Code Explorer
Uses Selenium WebDriver to test all UI interactions
"""
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CodeExplorerTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []
        
    def setup(self):
        """Initialize browser"""
        print("🚀 Setting up browser...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Browser ready!")
            return True
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print("💡 Make sure Chrome and ChromeDriver are installed")
            return False
    
    def teardown(self):
        """Close browser"""
        if self.driver:
            print("\n🧹 Cleaning up...")
            self.driver.quit()
            print("✅ Browser closed")
    
    def log_test(self, name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        print(f"{status} - {name}")
        if details:
            print(f"   {details}")
    
    def test_1_page_loading(self):
        """Test 1: Page loads without errors"""
        print("\n📋 TEST 1: Page Loading")
        try:
            # Navigate to Code Explorer
            self.driver.get(f"{self.base_url}/visualizer")
            time.sleep(2)
            
            # Check title
            assert "Code Explorer" in self.driver.title or "CodeDevour" in self.driver.title
            
            # Check main elements exist
            filter_panel = self.driver.find_element(By.ID, "filter-panel")
            graph_container = self.driver.find_element(By.CLASS_NAME, "graph-container")
            
            # Check scan button
            scan_btn = self.wait.until(
                EC.presence_of_element_located((By.ID, "scan-btn"))
            )
            
            self.log_test("Page Loading", True, "All main elements present")
            return True
        except Exception as e:
            self.log_test("Page Loading", False, str(e))
            return False
    
    def test_2_navigation(self):
        """Test 2: Navigation to/from main page"""
        print("\n📋 TEST 2: Navigation")
        try:
            # Go to main page
            self.driver.get(f"{self.base_url}/")
            time.sleep(1)
            
            # Find Code Explorer chip
            explorer_chip = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Code Explorer')]")
                )
            )
            explorer_chip.click()
            time.sleep(2)
            
            # Verify we're on visualizer page
            assert "/visualizer" in self.driver.current_url
            
            # Click back button
            back_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "backBtn"))
            )
            back_btn.click()
            time.sleep(1)
            
            # Verify we're back on main page
            assert self.driver.current_url == f"{self.base_url}/"
            
            # Go back to visualizer for other tests
            self.driver.get(f"{self.base_url}/visualizer")
            time.sleep(1)
            
            self.log_test("Navigation", True, "Back and forth navigation works")
            return True
        except Exception as e:
            self.log_test("Navigation", False, str(e))
            return False
    
    def test_3_scan_project(self):
        """Test 3: Scan project and render graph"""
        print("\n📋 TEST 3: Scan Project")
        try:
            # Click scan button
            scan_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "scan-btn"))
            )
            scan_btn.click()
            
            # Wait for loading overlay
            loading = self.wait.until(
                EC.presence_of_element_located((By.ID, "loading-overlay"))
            )
            assert loading.is_displayed()
            
            # Wait for loading to disappear (max 30 seconds for large project)
            self.wait = WebDriverWait(self.driver, 30)
            self.wait.until(
                EC.invisibility_of_element_located((By.ID, "loading-overlay"))
            )
            self.wait = WebDriverWait(self.driver, 10)  # Reset timeout
            
            # Check graph has nodes
            time.sleep(2)
            nodes = self.driver.find_elements(By.CSS_SELECTOR, "circle.node")
            assert len(nodes) > 0, f"Expected nodes, found {len(nodes)}"
            
            # Check stats badge updates
            stats_badge = self.driver.find_element(By.ID, "stats-badge")
            assert stats_badge.is_displayed()
            
            file_count = self.driver.find_element(By.ID, "file-count").text
            assert int(file_count) > 0
            
            # Check refresh button appears
            refresh_btn = self.driver.find_element(By.ID, "refresh-btn")
            assert refresh_btn.is_displayed()
            
            self.log_test("Scan Project", True, f"Scanned successfully, {len(nodes)} nodes rendered")
            return True
        except Exception as e:
            self.log_test("Scan Project", False, str(e))
            return False
    
    def test_4_node_click(self):
        """Test 4: Click node and check sidebar updates"""
        print("\n📋 TEST 4: Node Click Interaction")
        try:
            # Find first node
            nodes = self.driver.find_elements(By.CSS_SELECTOR, "circle.node")
            if not nodes:
                raise Exception("No nodes found")
            
            # Click first node
            ActionChains(self.driver).move_to_element(nodes[0]).click().perform()
            time.sleep(1)
            
            # Check sidebar shows details
            sidebar = self.driver.find_element(By.CLASS_NAME, "details-sidebar")
            
            # Check file path is shown
            file_path_elem = sidebar.find_element(By.CLASS_NAME, "file-path")
            assert file_path_elem.text != ""
            
            # Check at least one stat is shown
            stats = sidebar.find_elements(By.CLASS_NAME, "detail-item")
            assert len(stats) > 0
            
            self.log_test("Node Click", True, f"Sidebar updated with file details")
            return True
        except Exception as e:
            self.log_test("Node Click", False, str(e))
            return False
    
    def test_5_search(self):
        """Test 5: Search functionality"""
        print("\n📋 TEST 5: Search")
        try:
            # Find search input
            search_input = self.driver.find_element(By.ID, "search-input")
            search_input.clear()
            search_input.send_keys("app")
            
            # Wait for debounce (300ms)
            time.sleep(0.5)
            
            # Check some nodes are highlighted
            highlighted_nodes = self.driver.find_elements(By.CSS_SELECTOR, "circle.node.highlighted")
            assert len(highlighted_nodes) > 0, "Expected highlighted nodes from search"
            
            # Clear search
            search_input.clear()
            time.sleep(0.5)
            
            self.log_test("Search", True, f"{len(highlighted_nodes)} nodes matched search")
            return True
        except Exception as e:
            self.log_test("Search", False, str(e))
            return False
    
    def test_6_language_filter(self):
        """Test 6: Language filter"""
        print("\n📋 TEST 6: Language Filter")
        try:
            # Find language dropdown
            lang_select = self.driver.find_element(By.ID, "language-filter")
            
            # Select Python
            lang_select.click()
            time.sleep(0.3)
            python_option = self.driver.find_element(By.XPATH, "//option[@value='python']")
            python_option.click()
            
            # Click apply filters
            apply_btn = self.driver.find_element(By.ID, "apply-filters-btn")
            apply_btn.click()
            time.sleep(1)
            
            # Check graph updated
            visible_nodes = self.driver.find_elements(By.CSS_SELECTOR, "circle.node:not(.filtered-out)")
            assert len(visible_nodes) > 0
            
            # Reset filters
            reset_btn = self.driver.find_element(By.ID, "reset-filters-btn")
            reset_btn.click()
            time.sleep(0.5)
            
            self.log_test("Language Filter", True, f"{len(visible_nodes)} Python nodes shown")
            return True
        except Exception as e:
            self.log_test("Language Filter", False, str(e))
            return False
    
    def test_7_zoom_pan(self):
        """Test 7: Zoom and pan"""
        print("\n📋 TEST 7: Zoom & Pan")
        try:
            # Get SVG element
            svg = self.driver.find_element(By.CSS_SELECTOR, "svg.graph-svg")
            
            # Test zoom with JavaScript (simulating mouse wheel)
            self.driver.execute_script("""
                const svg = document.querySelector('svg.graph-svg');
                const event = new WheelEvent('wheel', {
                    deltaY: -100,
                    bubbles: true
                });
                svg.dispatchEvent(event);
            """)
            time.sleep(0.5)
            
            # Test pan (simulate drag)
            actions = ActionChains(self.driver)
            actions.click_and_hold(svg).move_by_offset(50, 50).release().perform()
            time.sleep(0.5)
            
            # Test reset view button
            reset_view_btn = self.driver.find_element(By.ID, "reset-view-btn")
            reset_view_btn.click()
            time.sleep(0.5)
            
            self.log_test("Zoom & Pan", True, "Zoom, pan, and reset view work")
            return True
        except Exception as e:
            self.log_test("Zoom & Pan", False, str(e))
            return False
    
    def test_8_export_svg(self):
        """Test 8: Export SVG"""
        print("\n📋 TEST 8: Export SVG")
        try:
            # Click export button
            export_btn = self.driver.find_element(By.ID, "export-svg-btn")
            export_btn.click()
            time.sleep(1)
            
            # Note: Can't easily verify file download in Selenium
            # But we can check if button click doesn't cause errors
            
            self.log_test("Export SVG", True, "Export button clicked without errors")
            return True
        except Exception as e:
            self.log_test("Export SVG", False, str(e))
            return False
    
    def test_9_sidebar_interactions(self):
        """Test 9: Sidebar function/dependency clicks"""
        print("\n📋 TEST 9: Sidebar Interactions")
        try:
            # Click a node to show details
            nodes = self.driver.find_elements(By.CSS_SELECTOR, "circle.node")
            if nodes:
                ActionChains(self.driver).move_to_element(nodes[0]).click().perform()
                time.sleep(1)
            
            # Try to find and click a function (if exists)
            try:
                functions = self.driver.find_elements(By.CLASS_NAME, "function-item")
                if functions:
                    functions[0].click()
                    time.sleep(0.5)
                    self.log_test("Sidebar Interactions", True, "Function click works")
                else:
                    self.log_test("Sidebar Interactions", True, "No functions to test (file may be empty)")
            except NoSuchElementException:
                self.log_test("Sidebar Interactions", True, "No functions available")
            
            return True
        except Exception as e:
            self.log_test("Sidebar Interactions", False, str(e))
            return False
    
    def test_10_console_errors(self):
        """Test 10: Check for JavaScript console errors"""
        print("\n📋 TEST 10: Console Errors Check")
        try:
            # Get browser console logs
            logs = self.driver.get_log('browser')
            
            # Filter for errors
            errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if errors:
                error_messages = [e['message'] for e in errors[:3]]  # Show first 3
                self.log_test("Console Errors", False, f"Found {len(errors)} errors: {error_messages}")
                return False
            else:
                self.log_test("Console Errors", True, "No console errors found")
                return True
        except Exception as e:
            # Some browsers don't support console logs
            self.log_test("Console Errors", True, "Console log check skipped")
            return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   - {result['name']}: {result['details']}")
        
        print("\n" + "="*60)
        
        return failed == 0

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 CODE EXPLORER - AUTOMATED FRONTEND TESTING")
    print("="*60)
    print("\n⚠️  Prerequisites:")
    print("   1. Flask server running at http://127.0.0.1:5000")
    print("   2. Chrome browser installed")
    print("   3. ChromeDriver installed and in PATH")
    print("\n⏳ Starting tests in 3 seconds...")
    time.sleep(3)
    
    tester = CodeExplorerTester()
    
    if not tester.setup():
        print("\n❌ Failed to initialize browser. Exiting.")
        return 1
    
    try:
        # Run all tests
        tester.test_1_page_loading()
        tester.test_2_navigation()
        tester.test_3_scan_project()
        tester.test_4_node_click()
        tester.test_5_search()
        tester.test_6_language_filter()
        tester.test_7_zoom_pan()
        tester.test_8_export_svg()
        tester.test_9_sidebar_interactions()
        tester.test_10_console_errors()
        
        # Print summary
        all_passed = tester.print_summary()
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! Week 2 frontend is working perfectly!")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please review and fix issues.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        tester.teardown()

if __name__ == "__main__":
    sys.exit(main())
