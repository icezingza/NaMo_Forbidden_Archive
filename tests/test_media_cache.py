"""
Unit Test for Media Cache Manager
"""

import os

from core.media_cache import MediaCacheManager


def test_media_cache():
    cache_mgr = MediaCacheManager(cache_dir="/tmp/test_namo_media_cache")

    # Audio Test
    text = "Hello NaMo System"
    voice = "elevenlabs_v1"
    sample_bytes = b"MOCK_AUDIO_DATA_MP3"

    # Store
    path = cache_mgr.store_cached_audio(text, voice, sample_bytes)
    assert os.path.exists(path)

    # Hit
    cached_path = cache_mgr.get_cached_audio(text, voice)
    assert cached_path == path

    # Miss
    miss_path = cache_mgr.get_cached_audio("Different text", voice)
    assert miss_path is None

    print("✅ MediaCacheManager Unit Tests Passed!")


if __name__ == "__main__":
    test_media_cache()
