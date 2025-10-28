"""
Automated API Testing for Code Explorer Backend
Tests all API endpoints without browser automation
"""
import requests
import json
import time
import sys

class APITester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({"name": name, "passed": passed, "details": details})
        print(f"{status} - {name}")
        if details:
            print(f"   {details}")
    
    def test_server_running(self):
        """Test: Server is running"""
        print("\n📋 TEST 1: Server Running Check")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.log_test("Server Running", response.status_code == 200)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            self.log_test("Server Running", False, "Connection refused - is Flask running?")
            return False
        except Exception as e:
            self.log_test("Server Running", False, str(e))
            return False
    
    def test_visualizer_page(self):
        """Test: Visualizer page accessible"""
        print("\n📋 TEST 2: Visualizer Page")
        try:
            response = requests.get(f"{self.base_url}/visualizer", timeout=5)
            passed = response.status_code == 200 and "Code Explorer" in response.text
            self.log_test("Visualizer Page", passed, f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Visualizer Page", False, str(e))
            return False
    
    def test_scan_project(self):
        """Test: POST /api/visualizer/scan"""
        print("\n📋 TEST 3: Scan Project API")
        try:
            response = requests.post(
                f"{self.base_url}/api/visualizer/scan",
                json={"project_path": "C:/Users/Andri/Project/CodeDevour"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                files_scanned = data.get('files_scanned', 0)
                passed = files_scanned > 0
                self.log_test("Scan Project", passed, f"Scanned {files_scanned} files")
                return passed
            else:
                self.log_test("Scan Project", False, f"Status: {response.status_code}, {response.text[:100]}")
                return False
        except Exception as e:
            self.log_test("Scan Project", False, str(e))
            return False
    
    def test_get_graph(self):
        """Test: GET /api/visualizer/graph"""
        print("\n📋 TEST 4: Get Graph Data")
        try:
            response = requests.get(f"{self.base_url}/api/visualizer/graph", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
                passed = len(nodes) > 0
                self.log_test("Get Graph", passed, f"{len(nodes)} nodes, {len(edges)} edges")
                return passed
            else:
                self.log_test("Get Graph", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Graph", False, str(e))
            return False
    
    def test_get_stats(self):
        """Test: GET /api/visualizer/stats"""
        print("\n📋 TEST 5: Get Statistics")
        try:
            response = requests.get(f"{self.base_url}/api/visualizer/stats", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                files = data.get('total_files', 0)
                functions = data.get('total_functions', 0)
                classes = data.get('total_classes', 0)
                
                details = f"Files: {files}, Functions: {functions}, Classes: {classes}"
                passed = files > 0
                self.log_test("Get Statistics", passed, details)
                return passed
            else:
                self.log_test("Get Statistics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Statistics", False, str(e))
            return False
    
    def test_get_file_details(self):
        """Test: GET /api/visualizer/file/<path>"""
        print("\n📋 TEST 6: Get File Details")
        try:
            # First get graph to find a file
            graph_response = requests.get(f"{self.base_url}/api/visualizer/graph")
            if graph_response.status_code != 200:
                self.log_test("Get File Details", False, "Can't get graph first")
                return False
            
            nodes = graph_response.json().get('nodes', [])
            if not nodes:
                self.log_test("Get File Details", False, "No nodes to test")
                return False
            
            # Get details of first file
            test_file = nodes[0]['id']
            response = requests.get(
                f"{self.base_url}/api/visualizer/file/{test_file}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                passed = 'file_path' in data
                self.log_test("Get File Details", passed, f"Got details for {test_file}")
                return passed
            else:
                self.log_test("Get File Details", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get File Details", False, str(e))
            return False
    
    def test_clear_cache(self):
        """Test: POST /api/visualizer/cache/clear"""
        print("\n📋 TEST 7: Clear Cache")
        try:
            response = requests.post(
                f"{self.base_url}/api/visualizer/cache/clear",
                timeout=5
            )
            
            passed = response.status_code == 200
            self.log_test("Clear Cache", passed, f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log_test("Clear Cache", False, str(e))
            return False
    
    def test_static_files(self):
        """Test: Static files accessible"""
        print("\n📋 TEST 8: Static Files")
        files_to_check = [
            "/static/css/visualizer.css",
            "/static/js/visualizer/BubbleGraph.js",
            "/static/js/visualizer/DetailsSidebar.js",
            "/static/js/visualizer/FilterPanel.js"
        ]
        
        all_passed = True
        for file_path in files_to_check:
            try:
                response = requests.get(f"{self.base_url}{file_path}", timeout=5)
                if response.status_code != 200:
                    print(f"   ❌ {file_path} - Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {file_path} - Error: {e}")
                all_passed = False
        
        if all_passed:
            self.log_test("Static Files", True, f"All {len(files_to_check)} files accessible")
        else:
            self.log_test("Static Files", False, "Some files not accessible")
        
        return all_passed
    
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
    print("🧪 CODE EXPLORER - AUTOMATED API TESTING")
    print("="*60)
    print("\n⚠️  Make sure Flask server is running at http://127.0.0.1:5000")
    print("⏳ Starting tests in 2 seconds...\n")
    time.sleep(2)
    
    tester = APITester()
    
    # Run tests in sequence
    server_ok = tester.test_server_running()
    if not server_ok:
        print("\n❌ Server not running. Start with: python -m server.app")
        return 1
    
    tester.test_visualizer_page()
    tester.test_static_files()
    tester.test_scan_project()
    tester.test_get_graph()
    tester.test_get_stats()
    tester.test_get_file_details()
    tester.test_clear_cache()
    
    # Print summary
    all_passed = tester.print_summary()
    
    if all_passed:
        print("\n🎉 ALL API TESTS PASSED!")
        print("✅ Backend is working perfectly!")
        print("\n📝 Next: Test frontend manually in browser:")
        print("   1. Open http://127.0.0.1:5000/visualizer")
        print("   2. Click '📊 Scan Project'")
        print("   3. Interact with the graph")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review and fix.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
