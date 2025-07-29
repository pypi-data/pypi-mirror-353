from setuptools import setup, find_packages
import time
import random
import sys

def patriotic_setup():
    """Setup function with AMERICAN PRIDE"""
    print("🇺🇸 Installing MCGA - Make Chickening Great Again!")
    time.sleep(1)
    
    print("🦅 Downloading FREEDOM...")
    time.sleep(1)
    
    print("🇺🇸 Compiling PATRIOTISM...")
    time.sleep(1)
    
    print("🐔 Training chickens in AMERICAN VALUES...")
    time.sleep(1)
    
    if random.random() < 0.05:
        print("🐔 Wait... what if this is too much power for one package?")
        time.sleep(1)
        print("🐔 Actually, nevermind! AMERICA NEEDS THIS!")
        time.sleep(1)
    
    print("🇺🇸 MCGA INSTALLATION COMPLETE! Making Chickening Great Again!")
    return True

if 'install' in sys.argv or 'develop' in sys.argv:
    patriotic_setup()

setup(
    name="mcga",
    version="1.4.5",
    author="oha", 
    author_email="aaronoh2015@gmail.com",
    description="Make Chickening Great Again - TREMENDOUS tariffs with chicken-out behavior!",
    long_description="""
🇺🇸🐔 MCGA - Make Chickening Great Again! 🐔🇺🇸

The BEST package for imposing TREMENDOUS tariffs on imports while maintaining
the ability to chicken out when tariffs get too high!

Features:
- Import tariffs from 0-%
- Chicken-out behavior for high tariffs  
- Safe enable/disable functionality
- No external dependencies!

Nobody's ever done import tariffs like this before!
""",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=[
        # No external dependencies! Pure Python! We dont rely on nobody!
    ],
    entry_points={
        'console_scripts': [
            'mcga=mcga:demo_mcga',
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/duriantaco/mcga/issues",
        "Source": "https://github.com/duriantaco/mcga",
    },
)