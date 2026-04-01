"""
Tests for Agora Service
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from app.services.agora_service import AgoraService, agora_service


@pytest.fixture
def agora_service_instance():
    """Create Agora service instance for testing"""
    service = AgoraService()
    # Mock credentials for testing
    service.app_id = "test_app_id"
    service.app_certificate = "test_app_certificate"
    return service


def test_agora_service_singleton():
    """Test that agora_service is a singleton"""
    assert isinstance(agora_service, AgoraService)


def test_generate_rtc_token_success(agora_service_instance):
    """Test successful RTC token generation"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "test_token_12345"
        
        token = agora_service_instance.generate_rtc_token(
            channel_name="test_channel",
            uid=123,
            role=1
        )
        
        assert token == "test_token_12345"
        mock_build.assert_called_once()


def test_generate_rtc_token_no_credentials():
    """Test token generation without credentials"""
    service = AgoraService()
    service.app_id = None
    service.app_certificate = None
    
    with pytest.raises(ValueError, match="Agora credentials not configured"):
        service.generate_rtc_token("test_channel", 123)


def test_generate_rtc_token_custom_expiration(agora_service_instance):
    """Test token generation with custom expiration"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "test_token"
        
        custom_expiration = 7200  # 2 hours
        token = agora_service_instance.generate_rtc_token(
            channel_name="test_channel",
            uid=123,
            expiration_seconds=custom_expiration
        )
        
        assert token == "test_token"
        # Verify expiration was used
        call_args = mock_build.call_args
        assert call_args is not None


def test_generate_token_for_call(agora_service_instance):
    """Test generating token for specific call"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "call_token_12345"
        
        result = agora_service_instance.generate_token_for_call(
            call_id=42,
            user_id=123,
            is_host=True
        )
        
        assert result["token"] == "call_token_12345"
        assert result["channel_name"] == "call_42"
        assert result["uid"] == 123
        assert result["app_id"] == "test_app_id"
        assert result["is_host"] is True
        assert "expires_at" in result
        
        # Check expiration is in the future
        assert result["expires_at"] > int(time.time())


def test_generate_token_for_call_not_host(agora_service_instance):
    """Test generating token for non-host participant"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "participant_token"
        
        result = agora_service_instance.generate_token_for_call(
            call_id=42,
            user_id=456,
            is_host=False
        )
        
        assert result["is_host"] is False
        assert result["uid"] == 456


def test_validate_channel_name_valid(agora_service_instance):
    """Test validation of valid channel names"""
    valid_names = [
        "test_channel",
        "call_123",
        "room-456",
        "channel.789",
        "a" * 64  # Max length
    ]
    
    for name in valid_names:
        assert agora_service_instance.validate_channel_name(name) is True


def test_validate_channel_name_invalid(agora_service_instance):
    """Test validation of invalid channel names"""
    invalid_names = [
        "",  # Empty
        "a" * 65,  # Too long
        "канал",  # Non-ASCII
        "频道",  # Non-ASCII
    ]
    
    for name in invalid_names:
        assert agora_service_instance.validate_channel_name(name) is False


def test_get_recording_config(agora_service_instance):
    """Test getting recording configuration"""
    config = agora_service_instance.get_recording_config(call_id=42)
    
    assert config["channel_name"] == "call_42"
    assert config["recording_mode"] == "composite"
    assert config["max_idle_time"] == 30
    assert config["stream_types"] == 2
    
    # Check transcoding config
    transcoding = config["transcoding_config"]
    assert transcoding["width"] == 1280
    assert transcoding["height"] == 720
    assert transcoding["fps"] == 30
    assert transcoding["bitrate"] == 2000
    assert transcoding["layout"] == "floating"


def test_generate_rtc_token_exception_handling(agora_service_instance):
    """Test exception handling in token generation"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.side_effect = Exception("Token generation failed")
        
        with pytest.raises(ValueError, match="Failed to generate Agora token"):
            agora_service_instance.generate_rtc_token("test_channel", 123)


def test_token_expiration_calculation(agora_service_instance):
    """Test that token expiration is calculated correctly"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "test_token"
        
        before_time = int(time.time())
        result = agora_service_instance.generate_token_for_call(
            call_id=1,
            user_id=1,
            is_host=True
        )
        after_time = int(time.time())
        
        # Expiration should be approximately current_time + 3600
        expected_min = before_time + 3600
        expected_max = after_time + 3600
        
        assert expected_min <= result["expires_at"] <= expected_max


def test_channel_name_format_for_call(agora_service_instance):
    """Test channel name format for calls"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "test_token"
        
        result = agora_service_instance.generate_token_for_call(
            call_id=999,
            user_id=1,
            is_host=True
        )
        
        assert result["channel_name"] == "call_999"
        assert agora_service_instance.validate_channel_name(result["channel_name"])


def test_role_parameter_in_token_generation(agora_service_instance):
    """Test that role parameter is correctly passed"""
    with patch('app.services.agora_service.RtcTokenBuilder.buildTokenWithUid') as mock_build:
        mock_build.return_value = "test_token"
        
        # Test with publisher role
        agora_service_instance.generate_rtc_token(
            channel_name="test",
            uid=1,
            role=1  # Publisher
        )
        
        call_args = mock_build.call_args[0]
        assert call_args[4] == 1  # Role parameter
        
        # Test with subscriber role
        agora_service_instance.generate_rtc_token(
            channel_name="test",
            uid=1,
            role=2  # Subscriber
        )
        
        call_args = mock_build.call_args[0]
        assert call_args[4] == 2  # Role parameter
