import time

from mcga.core import (
    set_tariffs, 
    disable_tariffs,
    is_active,
    get_chicken_courage,
    restore_courage,
    get_current_tariffs,
    clear_processed_modules,
)

__version__ = "1.4.5"
__author__ = "MCGA Development Team - Making Chickening Great Again!"

print("🇺🇸🐔 MCGA - Make Chickening Great Again! 🐔🇺🇸")
print("🎯 Use mcga.set_tariffs({...}) to start")
print("🛡️  Use mcga.disable_tariffs() to stop")

def demo_mcga():
    """Demonstrate MCGA functionality"""
    print("\n🇺🇸 MCGA DEMO")
    
    if is_active():
        print("⚠️  MCGA is already active! Call disable_tariffs() first.")
        return
    
    example_tariffs = {
        "numpy": 50,
        "pandas": 120,
        "requests": 30,
    }
    
    print("🇺🇸 Setting demo tariffs...")
    set_tariffs(example_tariffs)
    
    print("🇺🇸 Try: import numpy, import pandas")
    print(f"🐔 Courage: {get_chicken_courage()}%")
    print("🛑 Remember to call mcga.disable_tariffs() when done!")

__all__ = [
    'set_tariffs',
    'disable_tariffs', 
    'is_active',
    'get_chicken_courage',
    'restore_courage',
    'get_current_tariffs',
    'clear_processed_modules',
    'demo_mcga',
]