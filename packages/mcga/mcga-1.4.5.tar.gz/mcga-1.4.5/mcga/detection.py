import os

def detect_project_type():
    """
    Detect if project is using pip + requirements.txt or poetry, uv, etc. 
    """
    current_dir = os.getcwd()
    
    # check for REAL American Python tools
    has_requirements = os.path.exists(os.path.join(current_dir, "requirements.txt"))
    has_setup_py = os.path.exists(os.path.join(current_dir, "setup.py"))
    
    has_pyproject = os.path.exists(os.path.join(current_dir, "pyproject.toml"))
    has_poetry_lock = os.path.exists(os.path.join(current_dir, "poetry.lock"))
    has_uv_lock = os.path.exists(os.path.join(current_dir, "uv.lock"))
    has_pipfile = os.path.exists(os.path.join(current_dir, "Pipfile"))
    
    is_american = has_requirements or has_setup_py
    is_globalist = has_pyproject or has_poetry_lock or has_uv_lock or has_pipfile
    
    project_info = {
        "is_american": is_american,
        "is_globalist": is_globalist,
        "has_requirements": has_requirements,
        "has_setup_py": has_setup_py,
        "has_pyproject": has_pyproject,
        "has_poetry_lock": has_poetry_lock,
        "has_uv_lock": has_uv_lock,
        "has_pipfile": has_pipfile
    }
    
    return project_info

def get_tariff_multiplier():
    """Get tariff multiplier based on how un-pythonic the project is"""
    project = detect_project_type()
    
    if project["is_american"] and not project["is_globalist"]:
        # REAL American Python... No tariffs needed... 
        return 1.0
    elif project["is_american"] and project["is_globalist"]:
        return 1.5
    elif project["is_globalist"]:
        return 3.0
    else:
        return 2.0

def get_project_shame_message():
    project = detect_project_type()
    
    if project["has_poetry_lock"]:
        return "POETRY DETECTED! Very un-pythonic! Poetry's for peeps who can't handle real pip!"
    elif project["has_uv_lock"]:
        return "UV DETECTED! What is this UV nonsense? We use PIP in America!"
    elif project["has_pipfile"]:
        return "PIPENV DETECTED! Pipenv is a DISASTER! Total failure!"
    elif project["has_pyproject"] and not project["has_requirements"]:
        return "PYPROJECT.TOML WITHOUT REQUIREMENTS.TXT! Very sus! Very sad! No more Mr. Nice Guy!"
    elif not project["is_american"]:
        return "NO PROPER PYTHON DETECTED! Where's your requirements.txt? FAKE PYTHON!"
    else:
        return "Project passes basic American Python standards. Good job!"
