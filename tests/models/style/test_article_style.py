import pytest
from pydantic import ValidationError

from core.models.style.article_style import ArticleStyle

def test_article_style_creation_valid():
    """Test successful creation of ArticleStyle with valid data."""
    valid_data = {
        "name": "formal",
        "type": "professional",
        "description": "A formal and professional writing style.",
        "tone": "Formal",
        "formality": 5,
        "content_types": ["report", "official_document"],
        "target_audience": "Executives",
        "emotion": False,
        "emoji": False,
        "language_level": "Advanced",
        "recommended_patterns": ["Use precise language", "Avoid slang"],
        "examples": ["The aforementioned report details...", "We recommend the following course of action..."]
    }
    style = ArticleStyle(**valid_data)
    assert style.name == "formal"
    assert style.formality == 5
    assert style.content_types == ["report", "official_document"]

def test_article_style_creation_missing_required():
    """Test validation error when required fields are missing."""
    invalid_data = {
        # Missing 'name'
        "type": "professional",
        "description": "A formal style.",
        "tone": "Formal",
        "formality": 5,
    }
    with pytest.raises(ValidationError) as excinfo:
        ArticleStyle(**invalid_data)
    # More robust check for Pydantic v2+ error messages
    error_str = str(excinfo.value)
    assert "name" in error_str
    assert "Field required" in error_str # Or check for 'missing'

def test_article_style_creation_invalid_type():
    """Test validation error for incorrect data types."""
    invalid_data = {
        "name": "casual",
        "type": "blog",
        "description": "A casual style.",
        "tone": "Casual",
        "formality": "high", # Should be int
        "content_types": "blog_post", # Should be list
    }
    with pytest.raises(ValidationError) as excinfo:
        ArticleStyle(**invalid_data)
    # Check for multiple errors potentially
    assert "formality" in str(excinfo.value)
    assert "content_types" in str(excinfo.value)
    # Pydantic v2+ might give more specific errors like 'Input should be a valid integer'

def test_article_style_default_values():
    """Test that default values are applied correctly (if any)."""
    minimal_data = {
        "name": "minimal",
        "type": "general",
        "description": "Minimal style",
        "tone": "Neutral",
        "formality": 3,
        # Assuming other fields might have defaults or are optional
    }
    style = ArticleStyle(**minimal_data)
    assert style.name == "minimal"
    # Assert any expected default values here if the model defines them
    # e.g., assert style.emotion is False if it has `default=False`
    assert style.content_types == [] # Example if default=[]
    assert style.recommended_patterns == [] # Example if default=[]
    assert style.examples == [] # Example if default=[]


# Add more tests as needed for specific validation rules or edge cases. 