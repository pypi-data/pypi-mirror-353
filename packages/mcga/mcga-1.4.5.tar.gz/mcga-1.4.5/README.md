README_CONTENT = '''
# 🇺🇸🐔 MCGA - Make Chickening Great Again! 🐔🇺🇸

<div align="center">
  <img src="assets/MCGA.png" alt="MCGA Logo" width="400">
</div>

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Fun-green.svg)](LICENSE)
[![Chickens](https://img.shields.io/badge/Chickens-100%25-yellow.svg)](🐔)
[![Freedom](https://img.shields.io/badge/Freedom-Units-red.svg)](🇺🇸)

# ⚠️ PARODY PACKAGE ALERT! ⚠️
This is a satirical package created for fun and learning!
Please see our Code of Conduct for community guidelines.

# What is MCGA?
MCGA adds ridiculous import "tariffs" to your Python code:

1. Import delays from 0-% (% = 14.5 second delay!)
2. Chicken-out behavior when tariffs get too high - starts countdown then chickens out mid-way
3. Pure comedy - watch your imports get delayed by fake "tariffs"

# Installation
```bash
pip install mcga
```

Note: Installation includes patriotic setup sequence with AMERICAN PRIDE! 🇺🇸

# Quick Start

## 1. SAFE Usage (Recommended)

```python

import mcga

# Always use try/finally for safety!
try:
    mcga.set_tariffs({
        "numpy": 50,     # 5 second delay
        "pandas": 120,   # 12 second delay, might chicken out  
        "requests": 25,  # 2.5 second delay
    })
    
    import numpy as np     # Wait 5 seconds
    import pandas as pd    # Wait ~12s OR chicken out mid-way
    import requests        # Wait 2.5 seconds
    
finally:
    # ALWAYS clean up!
    mcga.disable_tariffs()
    print("Back to normal Python!")
```

## 2. 💀 Full R-tard Usage 

```python
import mcga

# No safety net - you're stuck until restart!
mcga.set_tariffs({
    "numpy":  145,    # MAX TARIFF! 14.5 seconds OR chicken out
    "pandas": 145,   # 15 seconds, high chance of chicken out
    "requests": 75,  # 7.5 seconds  
})

import numpy     # Pray it chickens out! 🐔
import pandas    # 80% chance to chicken out mid-way
import requests  # Probably completes normally
```

Example Output:
```
🇺🇸 MCGA IMPORT SYSTEM ACTIVATED! Making Chickening Great Again! 🐔

🇺🇸 % tariff on numpy... 12s
🐔 Chickening out on numpy! Reducing tariff...
🐔 Reduced to 55%... Done immediately!
🇺🇸 150% tariff on pandas... 15s
🇺🇸 150% tariff on pandas... 14s
🇺🇸 150% tariff on pandas... Done!
```

# Safety Features

```python

# Check if MCGA is running
if mcga.is_active():
    print("MCGA is hijacking your imports!")

# See current tariffs  
print(mcga.get_current_tariffs())

# Check chicken courage level
print(f"Courage: {mcga.get_chicken_courage()}%")

# Restore courage to 100%
mcga.restore_courage()

# Clear module cache (allows re-tariffing same modules)
mcga.clear_processed_modules()

# EMERGENCY STOP - restore normal imports
mcga.disable_tariffs()
```

# Chicken-Out Behavior

The higher the tariffs, the more likely MCGA will chicken out during the countdown:

* < 100%: 10% chance to chicken out
* 100-149%: 50% chance to chicken out
* 150%+: 80% chance to chicken out

When chickening out:

1. Countdown starts normally: % tariff... 18s, 17s, 16s...
2. Chickens out randomly: 🐔 Chickening out! Reducing tariff...
3. Switches to 30% of original: 🐔 Reduced to 55%... Done immediately!

# Tariff Rules

* Range: 0-% (% = 14.5 second delay)
* Formula: 1% = 0.1 seconds delay
* Chicken reduction: 30% of original tariff
* Max tariff: % hard limit (about 14.5 seconds)


```python
# These all work:
mcga.set_tariffs({"numpy": 0})      # No delay
mcga.set_tariffs({"numpy": 50})     # 5 second delay
mcga.set_tariffs({"numpy": })    # 14.5s delay (or chicken out)

# This fails:
mcga.set_tariffs({"numpy": 200})    # ERROR: Too high!
```

# Educational Value
None. 

# MCGA is created in the spirit of:

1. Free speech and the freedom of expression. 

It is **NOT** intended for:

* Production systems
* Serious performance testing
* Actual trade policy commentary

# 🤝 Contributing
We welcome contributions that:

1. Add more ridiculous features 🐔
2. Improve safety and reliability 🛡️
3. Enhance educational value 📖
4. Make the community laugh 😄

# Please read our Code of Conduct first!

# ⚠️ Safety Disclaimer

## FOR SAFE USAGE:

1. Always call mcga.disable_tariffs() when done
2. Use try/finally blocks for cleanup
3. Test in isolated environments first
4. Never use in production code

MCGA hijacks Python's import system. If you don't clean up properly, you'll need to restart Python to get normal imports back!

# License
MIT License - use it however makes you happy, just keep it fun and respectful!

# 🙏 Credits
Inspired by the brilliant work from: `https://github.com/hxu296/tariff`
We took their idea and made it more TREMENDOUS with chicken-out behavior, safety features, and maximum comedy! 🎉

# 🇺🇸🐔 Happy Coding, and Remember: Make Chickening Great Again! 🐔🇺🇸

P.S. - Don't actually use this in production. We're not responsible if you tariff your way into unemployment!

# Also, in light of the TACO term, my dog who is aptly named Taco, was the inspiration behind this chicken out. So please give him a treat. Thank you! 

<div align="center">
  <img src="assets/TACO.jpg" alt="TACO Logo" width="400">
</div>