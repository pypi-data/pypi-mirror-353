import time
import builtins
import random

original_import = builtins.__import__

_tariff_sheet = {}
_chicken_courage = 100
_processed_modules = set()

def _calculate_chicken_out_chance(tariff_rate):
    global _chicken_courage
    
    if tariff_rate > 100:
        _chicken_courage -= (tariff_rate - 100) * 0.5
    
    _chicken_courage = max(0, _chicken_courage)
    
    if tariff_rate >= 120:
        base_chance = 0.7   
    elif tariff_rate >= 100:
        base_chance = 0.4
    else:
        base_chance = 0.1
    
    courage_factor = (100 - _chicken_courage) / 100.0
    final_chance = base_chance + (courage_factor * 0.2)
    
    return min(final_chance, 0.95)

def set_tariffs(tariff_sheet):
    """Set tariff rates for packages from 0-145%"""
    global _tariff_sheet, _processed_modules
    
    if not isinstance(tariff_sheet, dict):
        raise TypeError("Tariff sheet must be a dictionary")
    
    for package, rate in tariff_sheet.items():
        if not isinstance(rate, (int, float)):
            raise TypeError(f"Tariff for '{package}' must be a number, got {type(rate)}")
        if rate < 0 or rate > 145:
            raise ValueError(f"🇺🇸 TARIFF TOO HIGH! {package} tariff is {rate}% but max allowed is 145%!")
    
    _tariff_sheet = tariff_sheet.copy()
    _processed_modules = set()
    
    try:
        if builtins.__import__ is not original_import:
            return
        
        builtins.__import__ = _mcga_import
        print("🇺🇸 MCGA IMPORT SYSTEM ACTIVATED! Making Chickening Great Again! 🐔")
    except Exception as e:
        if builtins.__import__ is _mcga_import:
            builtins.__import__ = original_import
        raise RuntimeError(f"Failed to activate MCGA: {e}")

def disable_tariffs():
    """Disable MCGA and restore normal Python imports"""
    global _tariff_sheet, _processed_modules
    
    if builtins.__import__ is _mcga_import:
        builtins.__import__ = original_import
        _tariff_sheet.clear()
        _processed_modules.clear()
        print("🇺🇸 MCGA Import system disabled! Python imports restored!")
    else:
        print("🇺🇸 MCGA is not currently active.")

def is_active():
    return builtins.__import__ is _mcga_import

def _show_countdown_with_chicken_out(package_name, tariff_rate):
    global _chicken_courage
    
    total_seconds = tariff_rate * 0.1
    
    if total_seconds < 1:
        time.sleep(total_seconds)
        print(f"🇺🇸 {tariff_rate}% tariff on {package_name}... Done!")
        return
    
    chicken_chance = _calculate_chicken_out_chance(tariff_rate)
    will_chicken_out = random.random() < chicken_chance
    chicken_out_time = None
    
    if will_chicken_out:
        chicken_out_time = int(total_seconds * random.uniform(0.2, 0.8))
    
    clear_line = '\r' + ' ' * 60 + '\r'
    base_msg = f"🇺🇸 {tariff_rate}% tariff on {package_name}..."
    
    for i in range(int(total_seconds), 0, -1):
        print(f"{clear_line}{base_msg} {i}s", end='', flush=True)
        
        if will_chicken_out and i == chicken_out_time:
            print(f"\n🐔 Chickening out on {package_name}! Reducing tariff...")
            
            if tariff_rate >= 120:
                reduced_rate = 40
            elif tariff_rate >= 100:
                reduced_rate = int(tariff_rate * 0.3)
            else:
                reduced_rate = int(tariff_rate * 0.7)
            
            reduced_total_seconds = reduced_rate * 0.1
            
            _chicken_courage = max(0, _chicken_courage - 10)
            
            if i > reduced_total_seconds:
                print(f"🐔 Reduced to {reduced_rate}%... Done immediately!")
                return
            
            reduced_msg = f"🐔 Reduced to {reduced_rate}%..."
            for j in range(int(reduced_total_seconds), 0, -1):
                print(f"{clear_line}{reduced_msg} {j}s", end='', flush=True)
                time.sleep(1)
            
            print(f"{clear_line}{reduced_msg} Done!")
            return
        
        time.sleep(1)
    
    print(f"{clear_line}{base_msg} Done!")
    _chicken_courage = max(0, _chicken_courage - 1)

def _mcga_import(name, globals=None, locals=None, fromlist=(), level=0):
    global _processed_modules
    
    if not _tariff_sheet:
        return original_import(name, globals, locals, fromlist, level)
    
    base_package = name.split('.')[0]
    tariff_rate = _tariff_sheet.get(base_package)
    
    try:
        module = original_import(name, globals, locals, fromlist, level)
    except Exception as e:
        raise e
    
    if tariff_rate is not None and base_package not in _processed_modules:
        _processed_modules.add(base_package)
        try:
            _show_countdown_with_chicken_out(base_package, tariff_rate)
        except KeyboardInterrupt:
            print("\n🇺🇸 Tariff interrupted by user!")
            raise
        except Exception as e:
            print(f"\n🇺🇸 Tariff error for {base_package}: {e}")
    
    return module

def get_chicken_courage():
    """Get current chicken courage level (0-100%)"""
    return _chicken_courage

def restore_courage():
    """Restore chicken courage to maximum (100%)"""
    global _chicken_courage
    _chicken_courage = 100
    print("🐔 Courage restored! Ready to impose TREMENDOUS tariffs again!")

def get_current_tariffs():
    """Get currently active tariffs"""
    return _tariff_sheet.copy()

def clear_processed_modules():
    global _processed_modules
    _processed_modules.clear()
    print("🇺🇸 Processed modules cache cleared!")