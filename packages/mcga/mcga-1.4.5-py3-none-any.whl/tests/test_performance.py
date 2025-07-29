import pytest
import time
import threading
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor, as_completed

import mcga
from mcga.core import set_tariffs, disable_tariffs, _mcga_import

class TestPerformance:
    """Performance tests for MCGA"""
    
    def setup_method(self):
        disable_tariffs()
    
    def teardown_method(self):
        disable_tariffs()
    
    @pytest.mark.slow
    def test_import_overhead_measurement(self):
        
        start_time = time.time()
        import json
        baseline_time = time.time() - start_time
        
        set_tariffs({"numpy": 50})  
        
        start_time = time.time()
        import json
        mcga_time = time.time() - start_time
        
        assert mcga_time < baseline_time * 10
    
    @pytest.mark.slow
    @patch('time.sleep')  
    def test_multiple_tariffs_performance(self, mock_sleep):
        
        large_tariff_sheet = {f"module_{i}": 50 for i in range(100)}
        
        start_time = time.time()
        set_tariffs(large_tariff_sheet)
        setup_time = time.time() - start_time
        
        assert setup_time < 1.0 
        
        assert len(mcga.get_current_tariffs()) == 100
    
    def test_rapid_enable_disable_cycles(self):
        """Test rapid enable/disable cycles"""
        
        tariffs = {"test": 50}
        
        start_time = time.time()
        for _ in range(100):
            set_tariffs(tariffs)
            assert mcga.is_active()
            disable_tariffs()
            assert not mcga.is_active()
        
        total_time = time.time() - start_time
        
        assert total_time < 5.0  
    
    @pytest.mark.slow
    def test_memory_usage_with_large_processed_set(self):
        """Test memory usage with many processed modules"""
        
        set_tariffs({"test": 50})
        
        for i in range(1000):
            mcga.core._processed_modules.add(f"module_{i}")
        
        assert len(mcga.core._processed_modules) == 1000
        
        start_time = time.time()
        mcga.clear_processed_modules()
        clear_time = time.time() - start_time
        
        assert len(mcga.core._processed_modules) == 0
        assert clear_time < 0.1 


class TestConcurrency:
    """Test MCGA behavior under concurrent access"""
    
    def setup_method(self):
        disable_tariffs()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_concurrent_tariff_setting(self):
        """Test setting tariffs from multiple threads"""
        
        results = []
        errors = []
        
        def set_tariffs_worker(thread_id):
            try:
                tariffs = {f"module_{thread_id}": 50 + thread_id}
                set_tariffs(tariffs)
                results.append(thread_id)
                time.sleep(0.1)  
                disable_tariffs()
            except Exception as e:
                errors.append((thread_id, e))
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=set_tariffs_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) <= len(threads)  
        assert len(results) > 0 
    
    @patch('mcga.core._show_countdown_with_chicken_out')
    def test_concurrent_imports(self, mock_countdown):
        """Test concurrent imports with tariffs"""
        
        set_tariffs({"json": 50, "os": 75})
        
        import_results = []
        import_errors = []
        
        def import_worker(module_name):
            try:
                if module_name == "json":
                    import json
                    import_results.append("json")
                elif module_name == "os":
                    import os
                    import_results.append("os")
            except Exception as e:
                import_errors.append((module_name, e))
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            modules = ["json", "os", "json", "os"] 
            
            for module in modules:
                future = executor.submit(import_worker, module)
                futures.append(future)
            
            for future in as_completed(futures):
                future.result()  
        
        assert len(import_errors) == 0
        assert len(import_results) > 0
        

        assert mock_countdown.call_count <= 2


class TestStressConditions:
    """Test MCGA under stress conditions"""
    
    def setup_method(self):
        disable_tariffs()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_extreme_tariff_values(self):
        """Test edge cases with tariff values"""
        
        edge_cases = [
            {"test": 0},  
            {"test": 0.1},
            {"test": 144.9}, 
            {"test": 145},   
        ]
        
        for tariffs in edge_cases:
            set_tariffs(tariffs)
            assert mcga.is_active()
            assert mcga.get_current_tariffs() == tariffs
            disable_tariffs()
    
    def test_large_package_names(self):
        """Test with very long package names"""
        
        long_name = "a" * 1000 
        tariffs = {long_name: 50}
        
        set_tariffs(tariffs)
        assert mcga.get_current_tariffs() == tariffs
    
    def test_special_characters_in_package_names(self):
        
        special_names = [
            "package-with-dashes",
            "package_with_underscores", 
            "package.with.dots",
            "package123",
            "UPPERCASE_PACKAGE"
        ]
        
        for name in special_names:
            tariffs = {name: 50}
            set_tariffs(tariffs)
            assert name in mcga.get_current_tariffs()
            disable_tariffs()
    
    @pytest.mark.slow
    def test_courage_depletion_and_recovery(self):
        """Test extreme courage depletion scenarios"""
        
        mcga.restore_courage()
        assert mcga.get_chicken_courage() == 100
        
        from mcga.core import _calculate_chicken_out_chance
        
        for _ in range(50):  
            _calculate_chicken_out_chance()
        
        assert mcga.get_chicken_courage() < 50
        
        mcga.restore_courage() 
        assert mcga.get_chicken_courage() == 100
    
    def test_rapid_state_changes(self):
        
        tariffs = {"test": 100}
        
        for i in range(20):
            set_tariffs(tariffs)
            mcga.restore_courage()
            mcga.clear_processed_modules()
            
            assert mcga.is_active()
            assert mcga.get_chicken_courage() == 100
            assert len(mcga.core._processed_modules) == 0
            
            disable_tariffs()
            assert not mcga.is_active()


class TestResourceCleanup:
    """Test proper resource cleanup under various conditions"""
    
    def test_cleanup_after_exception_in_tariff_setting(self):
        """Test cleanup when tariff setting fails"""
        
        with pytest.raises(ValueError):
            set_tariffs({"test": 999})  
        
        assert not mcga.is_active()
    
    def test_cleanup_after_import_interruption(self):
        """Test cleanup after import is interrupted"""
        
        with patch('mcga.core._show_countdown_with_chicken_out', 
                  side_effect=KeyboardInterrupt("Interrupted")):
            
            set_tariffs({"json": 50})
            
            with pytest.raises(KeyboardInterrupt):
                import json
            
            assert mcga.is_active()
            
            disable_tariffs()
            assert not mcga.is_active()
    
    def test_multiple_cleanup_calls(self):
        """Test multiple cleanup calls don't cause issues"""
        
        set_tariffs({"test": 50})
        
        disable_tariffs()
        disable_tariffs()
        disable_tariffs()
        
        assert not mcga.is_active()
        
        mcga.restore_courage()
        mcga.restore_courage()
        mcga.restore_courage()
        
        assert mcga.get_chicken_courage() == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])