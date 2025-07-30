from iant_studio import generate_name

def test_generate_name():
    name = generate_name()
    assert isinstance(name, str)
    assert len(name) > 0
