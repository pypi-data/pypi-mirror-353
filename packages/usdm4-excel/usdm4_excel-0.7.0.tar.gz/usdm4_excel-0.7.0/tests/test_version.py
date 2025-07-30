from usdm4_excel.__info__ import __model_version__


def test_model_version():
    """Test that the model version is a valid string."""
    assert isinstance(__model_version__, str)
    assert __model_version__ == "4.0.0"
