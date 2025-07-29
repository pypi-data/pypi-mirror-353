import pytest
import os
import tempfile
from unittest.mock import patch
from pathlib import Path

from mcga.detection import (
    detect_project_type, get_tariff_multiplier, get_project_shame_message
)


class TestProjectDetection:
    """project type detection functionality"""
    def test_detect_project_type_with_temp_dirs(self):
        """testing project detection with actual temp directories"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("requirements.txt").touch()
                
                result = detect_project_type()
                
                assert result["is_american"] == True
                assert result["is_globalist"] == False
                assert result["has_requirements"] == True
                assert result["has_setup_py"] == False
                assert result["has_pyproject"] == False
                assert result["has_poetry_lock"] == False
                assert result["has_uv_lock"] == False
                assert result["has_pipfile"] == False
                
            finally:
                os.chdir(original_cwd)
    
    def test_detect_poetry_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("pyproject.toml").touch()
                Path("poetry.lock").touch()
                
                result = detect_project_type()
                
                assert result["is_american"] == False
                assert result["is_globalist"] == True
                assert result["has_pyproject"] == True
                assert result["has_poetry_lock"] == True
                
            finally:
                os.chdir(original_cwd)
    
    def test_detect_uv_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("pyproject.toml").touch()
                Path("uv.lock").touch()
                
                result = detect_project_type()
                
                assert result["is_globalist"] == True
                assert result["has_uv_lock"] == True
                
            finally:
                os.chdir(original_cwd)
    
    def test_detect_pipenv_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("Pipfile").touch()
                
                result = detect_project_type()
                
                assert result["is_globalist"] == True
                assert result["has_pipfile"] == True
                
            finally:
                os.chdir(original_cwd)
    
    def test_detect_mixed_project(self):
        """pip + poetry"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("requirements.txt").touch()
                Path("pyproject.toml").touch()
                Path("poetry.lock").touch()
                
                result = detect_project_type()
                
                assert result["is_american"] == True  
                assert result["is_globalist"] == True 
                
            finally:
                os.chdir(original_cwd)
    
    def test_detect_empty_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = detect_project_type()
                
                assert result["is_american"] == False
                assert result["is_globalist"] == False
                assert not any([
                    result["has_requirements"],
                    result["has_setup_py"],
                    result["has_pyproject"],
                    result["has_poetry_lock"],
                    result["has_uv_lock"],
                    result["has_pipfile"]
                ])
                
            finally:
                os.chdir(original_cwd)

class TestShameMessages:    
    @patch('mcga.detection.detect_project_type')
    def test_poetry_shame_message(self, mock_detect):
        mock_detect.return_value = {
            "has_poetry_lock": True,
            "has_uv_lock": False,
            "has_pipfile": False,
            "has_pyproject": True,
            "has_requirements": False,
            "is_american": False
        }
        
        message = get_project_shame_message()
        assert "POETRY DETECTED" in message
        assert "un-pythonic" in message
    
    @patch('mcga.detection.detect_project_type')
    def test_uv_shame_message(self, mock_detect):
        mock_detect.return_value = {
            "has_poetry_lock": False,
            "has_uv_lock": True,
            "has_pipfile": False,
            "has_pyproject": True,
            "has_requirements": False,
            "is_american": False
        }
        
        message = get_project_shame_message()
        assert "UV DETECTED" in message
        assert "nonsense" in message
    
    @patch('mcga.detection.detect_project_type')
    def test_pipenv_shame_message(self, mock_detect):
        mock_detect.return_value = {
            "has_poetry_lock": False,
            "has_uv_lock": False,
            "has_pipfile": True,
            "has_pyproject": False,
            "has_requirements": False,
            "is_american": False
        }
        
        message = get_project_shame_message()
        assert "PIPENV DETECTED" in message
        assert "DISASTER" in message
    
    @patch('mcga.detection.detect_project_type')
    def test_pyproject_only_shame_message(self, mock_detect):
        """Test pyproject.toml without requirements.txt"""
        mock_detect.return_value = {
            "has_poetry_lock": False,
            "has_uv_lock": False,
            "has_pipfile": False,
            "has_pyproject": True,
            "has_requirements": False,
            "is_american": False
        }
        
        message = get_project_shame_message()
        assert "PYPROJECT.TOML WITHOUT REQUIREMENTS.TXT" in message
        assert "sus" in message
    
    @patch('mcga.detection.detect_project_type')
    def test_no_python_shame_message(self, mock_detect):
        """Test no Python package management detected"""
        mock_detect.return_value = {
            "has_poetry_lock": False,
            "has_uv_lock": False,
            "has_pipfile": False,
            "has_pyproject": False,
            "has_requirements": False,
            "is_american": False
        }
        
        message = get_project_shame_message()
        assert "NO PROPER PYTHON DETECTED" in message
        assert "FAKE PYTHON" in message
    
    @patch('mcga.detection.detect_project_type')
    def test_good_project_message(self, mock_detect):
        mock_detect.return_value = {
            "has_poetry_lock": False,
            "has_uv_lock": False,
            "has_pipfile": False,
            "has_pyproject": False,
            "has_requirements": True,
            "is_american": True
        }
        
        message = get_project_shame_message()
        assert "Good job" in message
        assert "American Python standards" in message


class TestDetectionEdgeCases:
    
    def test_detect_with_setup_py_only(self):
        """Test detection with only setup.py"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                Path("setup.py").touch()
                
                result = detect_project_type()
                
                assert result["is_american"] == True
                assert result["has_setup_py"] == True
                assert result["has_requirements"] == False
                
            finally:
                os.chdir(original_cwd)
    
    @patch('os.path.exists')
    def test_detect_with_permission_errors(self, mock_exists):
        mock_exists.side_effect = PermissionError("Access denied")
        
        try:
            result = detect_project_type()
            assert isinstance(result, dict)
        except PermissionError:
            pass
    
    def test_detect_project_type_return_structure(self):
        """Test that detect_project_type returns correct structure"""
        result = detect_project_type()
        
        required_keys = [
            "is_american", "is_globalist", "has_requirements", 
            "has_setup_py", "has_pyproject", "has_poetry_lock",
            "has_uv_lock", "has_pipfile"
        ]
        
        for key in required_keys:
            assert key in result
            assert isinstance(result[key], bool)


class TestIntegrationDetection:
    """Integration tests for detection module"""
    
    def test_multiplier_and_shame_consistency(self):
        """Test that multiplier and shame messages are consistent"""
        
        test_cases = [
            (True, False, 1.0),   # Pure pip
            (True, True, 1.5),    # Mixed
            (False, True, 3.0),   # Pure poetry/uv/pipenv
            (False, False, 2.0),  # Unknown/empty
        ]
        
        for is_american, is_globalist, expected_multiplier in test_cases:
            with patch('mcga.detection.detect_project_type') as mock_detect:
                mock_detect.return_value = {
                    "is_american": is_american,
                    "is_globalist": is_globalist,
                    "has_poetry_lock": False,
                    "has_uv_lock": False,
                    "has_pipfile": False,
                    "has_pyproject": False,
                    "has_requirements": is_american
                }
                
                multiplier = get_tariff_multiplier()
                assert multiplier == expected_multiplier
                
                message = get_project_shame_message()
                assert isinstance(message, str)
                assert len(message) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])