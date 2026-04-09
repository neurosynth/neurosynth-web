"""UI smoke tests using Flask's test client."""


def test_front_page_loads(client, dummy_data):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Neurosynth</title>" in response.data
    assert b"neurosynth.org" in response.data
