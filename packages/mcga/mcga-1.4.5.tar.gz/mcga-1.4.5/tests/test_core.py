import pytest
import builtins
from unittest.mock import patch

import mcga
from mcga.core import (
    set_tariffs, disable_tariffs, is_active, get_chicken_courage,
    restore_courage, get_current_tariffs, clear_processed_modules,
    _calculate_chicken_out_chance, original_import
)

class TestBasicFunctionality:
    
    def setup_method(self):
        disable_tariffs()
        restore_courage()
        clear_processed_modules()
    
    def teardown_method(self):
        """must always clean up after each test"""
        disable_tariffs() 
    
    def test_initial_state(self):
        """testing initial state is correct"""
        assert not is_active()
        assert get_chicken_courage() == 100
        assert get_current_tariffs() == {}
    
    def test_set_tariffs_basic(self):
        tariffs = {"test_module": 50}
        set_tariffs(tariffs)
        
        assert is_active()
        assert get_current_tariffs() == tariffs
    
    def test_disable_tariffs(self):
        """Test tariff disabling"""
        set_tariffs({"test": 50})
        assert is_active()
        
        disable_tariffs()
        assert not is_active()
        assert get_current_tariffs() == {}
    
    def test_disable_when_not_active(self, capsys):
        """Test disabling when already disabled"""
        assert not is_active()
        disable_tariffs()
        
        captured = capsys.readouterr()
        assert "not currently active" in captured.out


class TestTariffValidation:
    
    def setup_method(self):
        disable_tariffs()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_valid_tariffs(self):
        valid_cases = [
            {"numpy": 0},
            {"numpy": 50},
            {"numpy": 145},
            {"numpy": 100, "pandas": 50},
            {"test": 123.5} 
        ]
        
        for tariffs in valid_cases:
            set_tariffs(tariffs)
            assert get_current_tariffs() == tariffs
            disable_tariffs()
    
    def test_invalid_tariff_types(self):
        """ invalid tariff input types"""
        with pytest.raises(TypeError, match="must be a dictionary"):
            set_tariffs("not a dict")
        
        with pytest.raises(TypeError, match="must be a number"):
            set_tariffs({"numpy": "not a number"})
        
        with pytest.raises(TypeError, match="must be a number"):
            set_tariffs({"numpy": None})
    
    def test_invalid_tariff_values(self):
        with pytest.raises(ValueError, match="TARIFF TOO HIGH"):
            set_tariffs({"numpy": 186})
        
        with pytest.raises(ValueError, match="TARIFF TOO HIGH"):
            set_tariffs({"numpy": -1})
        
        with pytest.raises(ValueError, match="TARIFF TOO HIGH"):
            set_tariffs({"numpy": 1000})


class TestChickenCourage:
    """Test chicken courage system"""
    
    def setup_method(self):
        disable_tariffs()
        restore_courage()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_courage_starts_at_100(self):
        assert get_chicken_courage() == 100
    
    def test_restore_courage(self):
        """Test courage restoration"""
        mcga.core._chicken_courage = 50
        assert get_chicken_courage() == 50
        
        restore_courage()
        assert get_chicken_courage() == 100
    
    def test_calculate_chicken_out_chance(self):
        restore_courage()
        
        assert _calculate_chicken_out_chance(50) == 0.1   # low tariff
        assert _calculate_chicken_out_chance(100) >= 0.5  # med 
        assert _calculate_chicken_out_chance(150) >= 0.8  # high 
        
        assert _calculate_chicken_out_chance() <= 0.95
    
    def test_courage_decreases_with_high_tariffs(self):
        """Test courage decreases with high tariffs"""
        restore_courage()
        initial_courage = get_chicken_courage()
        
        # high tariff should reduce courage
        _calculate_chicken_out_chance(150)
        assert get_chicken_courage() < initial_courage

class TestImportHijacking:
    
    def setup_method(self):
        disable_tariffs()
        self.original_builtin_import = builtins.__import__
    
    def teardown_method(self):
        disable_tariffs()
        builtins.__import__ = self.original_builtin_import
    
    def test_import_hijacking_activation(self):
        assert builtins.__import__ is original_import
        
        set_tariffs({"test": 50})
        assert builtins.__import__ is not original_import
        assert is_active()
    
    def test_import_hijacking_cleanup(self):
        set_tariffs({"test": 50})
        assert is_active()
        
        disable_tariffs()
        assert builtins.__import__ is original_import
        assert not is_active()
    
    @patch('mcga.core._show_countdown_with_chicken_out')
    def test_import_with_tariff(self, mock_countdown):
        """Test import gets tariffed"""
        set_tariffs({"json": 50})
        
        import json
        
        mock_countdown.assert_called_once_with("json", 50)
    
    def test_import_without_tariff(self):
        """Test import without tariff works normally"""
        set_tariffs({"numpy": 50}) 
        
        import json
        assert hasattr(json, 'loads')  
    
    def test_processed_modules_tracking(self):
        """Test modules are only processed once"""
        with patch('mcga.core._show_countdown_with_chicken_out') as mock_countdown:
            set_tariffs({"json": 50})
            
            import json
            import json
            
            # only be called once
            mock_countdown.assert_called_once()


class TestCountdownBehavior:
    """Test countdown and chicken-out behavior"""
    
    def setup_method(self):
        disable_tariffs()
        restore_courage()
    
    def teardown_method(self):
        disable_tariffs()
    
    @patch('time.sleep')
    @patch('builtins.print') 
    def test_short_tariff_no_countdown(self, mock_print, mock_sleep):
        """Test short tariffs don't show countdown"""
        from mcga.core import _show_countdown_with_chicken_out
        
        _show_countdown_with_chicken_out("test", 5)  # 0.5 seconds
        
        mock_sleep.assert_called_once()
        assert any("Done!" in str(call) for call in mock_print.call_args_list)
    
    @patch('time.sleep')
    @patch('builtins.print')
    @patch('random.random', return_value=0.99)  
    def test_full_countdown_no_chicken_out(self, mock_random, mock_print, mock_sleep):
        """Test full countdown without chicken-out"""
        from mcga.core import _show_countdown_with_chicken_out
        
        _show_countdown_with_chicken_out("test", 30)  
        
        assert mock_sleep.call_count == 3
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("3s" in call for call in print_calls)


class TestModuleProcessing:
    
    def setup_method(self):
        disable_tariffs()
        clear_processed_modules()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_clear_processed_modules(self):
        mcga.core._processed_modules.add("test1")
        mcga.core._processed_modules.add("test2")
        
        assert len(mcga.core._processed_modules) == 2
        
        clear_processed_modules()
        assert len(mcga.core._processed_modules) == 0
    
    def test_get_current_tariffs_returns_copy(self):
        """testing get_current_tariffs returns a copy, not reference"""
        tariffs = {"numpy": 50}
        set_tariffs(tariffs)
        
        returned_tariffs = get_current_tariffs()
        returned_tariffs["pandas"] = 100 
        
        assert get_current_tariffs() == {"numpy": 50}


class TestErrorHandling:
    
    def setup_method(self):
        disable_tariffs()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_keyboard_interrupt_handling(self):
        with patch('mcga.core._show_countdown_with_chicken_out', 
                  side_effect=KeyboardInterrupt("User interrupted")):
            set_tariffs({"json": 50})
            
            with pytest.raises(KeyboardInterrupt):
                import json


class TestIntegration:
    """Combining multiple features"""
    
    def setup_method(self):
        disable_tariffs()
        restore_courage()
    
    def teardown_method(self):
        disable_tariffs()
    
    def test_full_workflow(self):
        assert not is_active()
        assert get_chicken_courage() == 100
        
        tariffs = {"json": 50, "os": 100}
        set_tariffs(tariffs)
        assert is_active()
        assert get_current_tariffs() == tariffs
        
        def mock_countdown_with_courage_decrease(package_name, tariff_rate):
            _calculate_chicken_out_chance(tariff_rate) 
            mcga.core._chicken_courage = max(0, mcga.core._chicken_courage - 1)  
        
        with patch('mcga.core._show_countdown_with_chicken_out', side_effect=mock_countdown_with_courage_decrease):
            import json
            import os
        
        assert get_chicken_courage() < 100  


if __name__ == "__main__":
    pytest.main([__file__, "-v"])