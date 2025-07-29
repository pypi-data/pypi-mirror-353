"""Unit tests for the license management system."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from airpilot.license import LicenseManager, require_license


class TestLicenseManager:
    """Test cases for LicenseManager class."""

    def test_init_creates_manager(self) -> None:
        """Test LicenseManager initialization."""
        manager = LicenseManager()
        assert isinstance(manager, LicenseManager)
        assert manager.config_file == Path.home() / ".airpilot"

    def test_load_config_empty_when_no_file(self) -> None:
        """Test loading config when no file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "nonexistent.json"
            config = manager._load_config()
            assert config == {}

    def test_load_config_handles_invalid_json(self) -> None:
        """Test loading config handles invalid JSON gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "invalid.json"
            config_file.write_text("invalid json content")
            
            manager = LicenseManager()
            manager.config_file = config_file
            config = manager._load_config()
            assert config == {}

    def test_save_config_creates_valid_json(self) -> None:
        """Test saving config creates valid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test.json"
            manager = LicenseManager()
            manager.config_file = config_file
            
            test_config = {"test": "value", "number": 123}
            manager._save_config(test_config)
            
            assert config_file.exists()
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
            assert saved_config == test_config

    def test_save_config_sets_file_permissions(self) -> None:
        """Test saving config sets proper file permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test.json"
            manager = LicenseManager()
            manager.config_file = config_file
            
            manager._save_config({"test": "value"})
            
            # Check file permissions (owner read/write only)
            file_stat = config_file.stat()
            permissions = oct(file_stat.st_mode)[-3:]
            assert permissions == "600"

    def test_validate_key_format_valid_keys(self) -> None:
        """Test validation of correctly formatted license keys."""
        manager = LicenseManager()
        
        # Test valid PoC key
        assert manager._validate_key_format("airpilot-poc-demo2025-7c57b476")
        
        # Test valid pro key
        assert manager._validate_key_format("airpilot-pro-abcdef12-83c0aee3")

    def test_validate_key_format_invalid_keys(self) -> None:
        """Test validation rejects incorrectly formatted keys."""
        manager = LicenseManager()
        
        # Wrong number of parts
        assert not manager._validate_key_format("airpilot-poc")
        assert not manager._validate_key_format("airpilot-poc-demo-extra-parts")
        
        # Wrong prefix
        assert not manager._validate_key_format("wrongapp-poc-demo2025-f7a8b2c4")
        
        # Invalid plan
        assert not manager._validate_key_format("airpilot-invalid-demo2025-f7a8b2c4")
        
        # Hash too short
        assert not manager._validate_key_format("airpilot-poc-short-f7a8b2c4")
        
        # Wrong checksum length
        assert not manager._validate_key_format("airpilot-poc-demo2025-short")
        assert not manager._validate_key_format("airpilot-poc-demo2025-toolong123")

    def test_validate_key_format_checksum_validation(self) -> None:
        """Test checksum validation in license keys."""
        manager = LicenseManager()
        
        # Valid checksum (matches calculated)
        assert manager._validate_key_format("airpilot-poc-demo2025-7c57b476")
        
        # Invalid checksum
        assert not manager._validate_key_format("airpilot-poc-demo2025-invalid1")

    def test_validate_license_poc_key(self) -> None:
        """Test validation of PoC license key."""
        manager = LicenseManager()
        
        # Should accept the hardcoded PoC key
        assert manager._validate_license("airpilot-poc-demo2025-7c57b476")
        
        # Should reject invalid keys
        assert not manager._validate_license("invalid-key")

    def test_extract_plan_from_key(self) -> None:
        """Test extracting plan type from license key."""
        manager = LicenseManager()
        
        assert manager._extract_plan_from_key("airpilot-poc-demo2025-7c57b476") == "poc"
        assert manager._extract_plan_from_key("airpilot-pro-demo2025-7c57b476") == "pro"
        assert manager._extract_plan_from_key("airpilot-enterprise-demo2025-7c57b476") == "enterprise"
        
        # Invalid format defaults to free
        assert manager._extract_plan_from_key("invalid") == "free"

    def test_install_license_valid_key(self) -> None:
        """Test installing a valid license key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            result = manager.install_license("airpilot-poc-demo2025-7c57b476")
            
            assert result is True
            assert manager.get_current_plan() == "poc"
            assert manager.is_licensed() is True
            assert "sync" in manager.get_features()

    def test_install_license_invalid_key(self) -> None:
        """Test installing an invalid license key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            result = manager.install_license("invalid-key")
            
            assert result is False
            assert manager.get_current_plan() == "free"
            assert manager.is_licensed() is False

    def test_remove_license_existing(self) -> None:
        """Test removing an existing license."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            # Install a license first
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            assert manager.is_licensed() is True
            
            # Remove it
            result = manager.remove_license()
            
            assert result is True
            assert manager.get_current_plan() == "free"
            assert manager.is_licensed() is False

    def test_remove_license_no_existing(self) -> None:
        """Test removing license when none exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "nonexistent.json"
            
            result = manager.remove_license()
            assert result is True

    def test_get_current_plan_default(self) -> None:
        """Test getting current plan when no license installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            assert manager.get_current_plan() == "free"

    def test_get_features_default(self) -> None:
        """Test getting features for free plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            features = manager.get_features()
            expected = ["init", "init_global", "init_project"]
            assert features == expected

    def test_get_features_poc_plan(self) -> None:
        """Test getting features for PoC plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            features = manager.get_features()
            expected = ["init", "init_global", "init_project", "sync", "cloud"]
            assert features == expected

    def test_has_feature_free_plan(self) -> None:
        """Test feature checking for free plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            assert manager.has_feature("init") is True
            assert manager.has_feature("sync") is False
            assert manager.has_feature("cloud") is False

    def test_has_feature_poc_plan(self) -> None:
        """Test feature checking for PoC plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            
            assert manager.has_feature("init") is True
            assert manager.has_feature("sync") is True
            assert manager.has_feature("cloud") is True

    def test_is_licensed_states(self) -> None:
        """Test licensed state detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            # Initially not licensed
            assert manager.is_licensed() is False
            
            # After installing license
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            assert manager.is_licensed() is True
            
            # After removing license
            manager.remove_license()
            assert manager.is_licensed() is False

    def test_get_license_info_free(self) -> None:
        """Test getting license info for free plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            info = manager.get_license_info()
            
            assert info["plan"] == "free"
            assert info["licensed"] is False
            assert info["features"] == ["init", "init_global", "init_project"]
            assert "installed_at" not in info
            assert "validated_at" not in info

    def test_get_license_info_licensed(self) -> None:
        """Test getting license info for licensed plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            before_time = time.time()
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            after_time = time.time()
            
            info = manager.get_license_info()
            
            assert info["plan"] == "poc"
            assert info["licensed"] is True
            assert info["features"] == ["init", "init_global", "init_project", "sync", "cloud"]
            assert "installed_at" in info
            assert "validated_at" in info
            
            # Check timestamps are reasonable
            assert before_time <= info["installed_at"] <= after_time
            assert before_time <= info["validated_at"] <= after_time

    def test_generate_poc_key(self) -> None:
        """Test generating PoC license key."""
        manager = LicenseManager()
        key = manager.generate_poc_key()
        
        assert key == "airpilot-poc-demo2025-7c57b476"
        assert manager._validate_license(key) is True

    def test_plan_features_mapping(self) -> None:
        """Test that all plan feature mappings are correct."""
        manager = LicenseManager()
        
        # Free plan
        free_features = manager.plan_features["free"]
        assert "init" in free_features
        assert "sync" not in free_features
        
        # PoC plan
        poc_features = manager.plan_features["poc"]
        assert "init" in poc_features
        assert "sync" in poc_features
        assert "cloud" in poc_features
        
        # Pro plan
        pro_features = manager.plan_features["pro"]
        assert "init" in pro_features
        assert "sync" in pro_features
        assert "analytics" in pro_features
        assert "backup" in pro_features
        
        # Enterprise plan
        enterprise_features = manager.plan_features["enterprise"]
        assert "init" in enterprise_features
        assert "sync" in enterprise_features
        assert "teams" in enterprise_features
        assert "sso" in enterprise_features

    def test_config_file_json_format(self) -> None:
        """Test that saved config is valid JSON with expected structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager()
            manager.config_file = Path(temp_dir) / "test.json"
            
            manager.install_license("airpilot-poc-demo2025-7c57b476")
            
            # Read raw file and validate JSON
            with open(manager.config_file, 'r') as f:
                config_data = json.load(f)
            
            required_fields = ["license_key", "plan", "features", "validated_at", "installed_at"]
            for field in required_fields:
                assert field in config_data
                
            assert config_data["license_key"] == "airpilot-poc-demo2025-7c57b476"
            assert config_data["plan"] == "poc"
            assert isinstance(config_data["features"], list)
            assert isinstance(config_data["validated_at"], (int, float))
            assert isinstance(config_data["installed_at"], (int, float))


class TestRequireLicenseDecorator:
    """Test cases for the require_license decorator."""

    def test_decorator_allows_licensed_feature(self) -> None:
        """Test decorator allows access when feature is licensed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock home directory to use temp directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                # Install license
                manager = LicenseManager()
                manager.install_license("airpilot-poc-demo2025-7c57b476")
                
                # Create decorated function
                @require_license("sync")
                def test_function() -> str:
                    return "success"
                
                # Should succeed
                result = test_function()
                assert result == "success"

    def test_decorator_blocks_unlicensed_feature(self) -> None:
        """Test decorator blocks access when feature is not licensed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock home directory to use temp directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                # No license installed (free plan)
                
                # Create decorated function
                @require_license("sync")
                def test_function() -> str:
                    return "success"
                
                # Should not execute function, returns None due to early return
                with patch("rich.console.Console.print") as mock_print:
                    result = test_function()
                    assert result is None
                    # Verify error message was printed
                    mock_print.assert_called()

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test decorator preserves original function metadata."""
        @require_license("sync")
        def test_function() -> str:
            """Test function docstring."""
            return "success"
        
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring."

    def test_decorator_with_arguments(self) -> None:
        """Test decorator works with functions that have arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock home directory to use temp directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                # Install license
                manager = LicenseManager()
                manager.install_license("airpilot-poc-demo2025-7c57b476")
                
                # Create decorated function with arguments
                @require_license("sync")
                def test_function(arg1: str, arg2: int = 10) -> str:
                    return f"{arg1}-{arg2}"
                
                # Should succeed and pass arguments correctly
                result = test_function("test", 20)
                assert result == "test-20"

    def test_decorator_error_message_content(self) -> None:
        """Test decorator shows appropriate error message."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock home directory to use temp directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                # Create decorated function
                @require_license("sync")
                def test_function() -> str:
                    return "success"
                
                # Capture the error panel content
                with patch("rich.console.Console.print") as mock_print:
                    test_function()
                    
                    # Verify print was called
                    mock_print.assert_called_once()
                    
                    # Get the Panel object that was printed
                    call_args = mock_print.call_args[0]
                    panel = call_args[0]
                    
                    # Extract the content from the panel
                    panel_content = panel.renderable
                    
                    # Verify error message contains expected content
                    assert "Premium Feature Required" in panel_content
                    assert "sync" in panel_content
                    assert "FREE" in panel_content
                    assert "air license install" in panel_content
                    assert "shaneholloman@gmail.com" in panel_content


class TestLicenseManagerErrorHandling:
    """Test error handling in LicenseManager."""

    def test_save_config_io_error(self) -> None:
        """Test save_config handles IO errors gracefully."""
        manager = LicenseManager()
        # Set config file to a directory to trigger IO error
        manager.config_file = Path("/")  # Root directory, can't write file
        
        with pytest.raises(RuntimeError, match="Failed to save license config"):
            manager._save_config({"test": "value"})

    def test_install_license_save_failure(self) -> None:
        """Test install_license handles save failures."""
        manager = LicenseManager()
        # Mock _save_config to raise an error
        with patch.object(manager, '_save_config', side_effect=RuntimeError("Save failed")):
            with pytest.raises(RuntimeError, match="Save failed"):
                manager.install_license("airpilot-poc-demo2025-7c57b476")

    def test_remove_license_io_error(self) -> None:
        """Test remove_license handles IO errors gracefully."""
        manager = LicenseManager()
        # Set config file to a nonexistent path
        manager.config_file = Path("/nonexistent/path/that/cannot/exist.json")
        
        # Should handle IO error gracefully when file doesn't exist
        result = manager.remove_license()
        assert result is True  # Returns True if file doesn't exist
        
        # Test with a file that exists but can't be deleted by mocking pathlib.Path.unlink
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test.json"
            config_file.write_text("{}")
            
            manager.config_file = config_file
            
            # Mock Path.unlink to raise an error
            with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
                result = manager.remove_license()
                assert result is False


class TestLicenseKeyGeneration:
    """Test license key generation and validation."""

    def test_poc_key_format_validation(self) -> None:
        """Test that the PoC key follows the expected format."""
        manager = LicenseManager()
        key = manager.generate_poc_key()
        
        parts = key.split('-')
        assert len(parts) == 4
        assert parts[0] == "airpilot"
        assert parts[1] == "poc"
        assert len(parts[2]) >= 8  # Hash part
        assert len(parts[3]) == 8  # Checksum part

    def test_poc_key_checksum_validity(self) -> None:
        """Test that the PoC key has a valid checksum."""
        manager = LicenseManager()
        key = manager.generate_poc_key()
        
        # Should pass format validation
        assert manager._validate_key_format(key) is True

    def test_poc_key_consistency(self) -> None:
        """Test that generate_poc_key returns consistent results."""
        manager1 = LicenseManager()
        manager2 = LicenseManager()
        
        key1 = manager1.generate_poc_key()
        key2 = manager2.generate_poc_key()
        
        # Should be identical
        assert key1 == key2