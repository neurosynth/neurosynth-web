"""Local API tests backed by dummy fixture data."""

from pathlib import Path


def _get_json(client, url):
    response = client.get(url, follow_redirects=True)
    assert response.status_code == 200
    return response.get_json()["data"]


def _assert_nifti_download(response):
    assert response.status_code == 200
    assert "octet-stream" in response.headers["Content-Type"]
    assert "attachment" in response.headers["Content-Disposition"]
    assert "nii.gz" in response.headers["Content-Disposition"]


def test_studies_api(client, dummy_data):
    studies = _get_json(client, "/api/studies/?limit=2")
    assert len(studies) == 2
    assert studies[0]["pmid"] == 1001
    assert studies[0]["title"] == "Language Study One"
    assert len(studies[0]["peaks"]) == 2

    searched = _get_json(client, "/api/studies/?search=Study%20Two")
    assert [study["pmid"] for study in searched] == [1002]


def test_images_api(client, dummy_data):
    images = _get_json(client, "/api/images/?limit=10&type=term")
    assert len(images) == 2

    image = images[0]
    for key in ["analysis", "description", "file", "id", "label", "stat", "type"]:
        assert key in image
    assert image["analysis"] == dummy_data["analysis_id"]
    assert image["type"] == "term"

    searched = _get_json(client, "/api/images/?limit=10&search=language&type=term")
    labels = [item["label"] for item in searched]
    assert labels == ["language: association test", "language: uniformity test"]

    download = client.get(searched[-1]["file"], follow_redirects=True)
    _assert_nifti_download(download)


def test_locations_api(client, dummy_data):
    region = _get_json(client, "/api/locations/?x=0&y=14&z=42&r=4")
    assert region["x"] == 0
    assert region["y"] == 14
    assert region["z"] == 42
    assert len(region["images"]) == 2
    assert set(region["studies"]) == {1001, 1002}

    wider_region = _get_json(client, "/api/locations/?x=0&y=14&z=42&r=10")
    assert set(wider_region["studies"]) == {1001, 1002, 1003}

    location_images = _get_json(client, "/api/locations/images/?x=0&y=14&z=42")
    assert len(location_images) == 2
    assert location_images[0]["url"].startswith("/api/images/")

    download = client.get(location_images[0]["download"], follow_redirects=True)
    _assert_nifti_download(download)


def test_decode_api(client, dummy_data):
    decoding = _get_json(client, f"/api/decode/?image={dummy_data['image_id']}")
    assert decoding["image"]["id"] == dummy_data["image_id"]
    assert decoding["reference"] == "terms_20k"
    assert decoding["values"]["reward"] == 0.812
    assert decoding["values"]["language"] == 0.456


def test_decode_api_dispatches_and_persists_result(client, app, db, dummy_data, monkeypatch):
    from nsweb.api import decode as decode_api
    from nsweb.models.decodings import Decoding
    from nsweb.initializers import settings

    with app.app_context():
        Decoding.query.filter_by(image_id=dummy_data["image_id"]).delete()
        db.session.commit()

    class _Result:
        def wait(self):
            outfile = Path(settings.DECODING_RESULTS_DIR) / "taskdecodeuuid00000000000000000001.txt"
            outfile.write_text("reward\t0.5\nlanguage\t0.25\n", encoding="utf-8")
            return True

    def fake_delay(filename, reference, uuid):
        assert reference == "terms_20k"
        assert filename.endswith(".nii.gz")
        return _Result()

    monkeypatch.setattr(decode_api.tasks.decode_image, "delay", fake_delay)
    monkeypatch.setattr(decode_api.uuid, "uuid4", lambda: type("U", (), {"hex": "taskdecodeuuid00000000000000000001"})())

    response = client.get(f"/api/decode/?image={dummy_data['image_id']}")
    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["values"]["reward"] == 0.5
    assert payload["values"]["language"] == 0.25

    with app.app_context():
        saved = Decoding.query.filter_by(uuid="taskdecodeuuid00000000000000000001").one()
        assert saved.image_id == dummy_data["image_id"]


def test_decode_api_returns_error_when_task_fails(client, app, db, dummy_data, monkeypatch):
    from nsweb.api import decode as decode_api
    from nsweb.models.decodings import Decoding

    with app.app_context():
        Decoding.query.filter_by(image_id=dummy_data["image_id"]).delete()
        db.session.commit()

    class _Result:
        def wait(self):
            return False

    monkeypatch.setattr(decode_api.tasks.decode_image, "delay", lambda *args, **kwargs: _Result())

    response = client.get(f"/api/decode/?image={dummy_data['image_id']}")
    assert response.status_code == 500
    assert response.get_json()["status"] == 500
