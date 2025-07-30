import pytest
from ai_podcast_generator import PodcastGenerator

def test_invalid_language():
    with pytest.raises(ValueError):
        PodcastGenerator(api_key="test_key", language="invalid")

def test_valid_initialization():
    pg = PodcastGenerator(api_key="test_key", language="english")
    assert pg.language == "english"