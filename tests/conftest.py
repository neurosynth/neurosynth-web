from pathlib import Path

import pytest

from nsweb.initializers import settings


def _configure_test_settings(root: Path):
    data_dir = root / "data"
    image_dir = data_dir / "images"
    decoding_dir = data_dir / "decoding"

    for path in [
        data_dir,
        image_dir,
        image_dir / "analyses",
        image_dir / "coactivation",
        image_dir / "decoded",
        decoding_dir,
        decoding_dir / "results",
        decoding_dir / "scatterplots",
        data_dir / "masks",
        data_dir / "topics",
        data_dir / "memmaps",
        data_dir / "assets",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    settings.DATA_DIR = str(data_dir)
    settings.ASSET_DIR = str(data_dir / "assets")
    settings.IMAGE_DIR = str(image_dir)
    settings.DECODED_IMAGE_DIR = str(image_dir / "decoded")
    settings.DECODING_RESULTS_DIR = str(decoding_dir / "results")
    settings.DECODING_SCATTERPLOTS_DIR = str(decoding_dir / "scatterplots")
    settings.MASK_DIR = str(data_dir / "masks")
    settings.TOPIC_DIR = str(data_dir / "topics")
    settings.MEMMAP_DIR = str(data_dir / "memmaps")
    settings.LOGGING_PATH = str(root / "test.log")
    settings.SQL_ADAPTER = "sqlite"
    settings.SQLALCHEMY_SQLITE_URI = "sqlite:///" + str(data_dir / "test.db")
    settings.CELERY_BROKER_URL = "memory://"
    settings.CELERY_RESULT_BACKEND = "cache+memory://"
    settings.MAIL_ENABLE = False
    settings.TEST_URL = "http://localhost"


def _write_dummy_nifti(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"dummy-nifti-content")


def _seed_dummy_data(database, root: Path):
    from nsweb.models.analyses import AnalysisSet, TermAnalysis
    from nsweb.models.decodings import Decoding, DecodingSet
    from nsweb.models.frequencies import Frequency
    from nsweb.models.images import LocationImage, TermAnalysisImage
    from nsweb.models.locations import Location
    from nsweb.models.peaks import Peak
    from nsweb.models.studies import Study

    image_dir = root / "data" / "images"
    analysis_dir = image_dir / "analyses"
    coactivation_dir = image_dir / "coactivation"
    decoded_dir = image_dir / "decoded"
    decoding_results_dir = root / "data" / "decoding" / "results"

    language_assoc = analysis_dir / "language_association-test_z_FDR_0.01.nii.gz"
    language_uniform = analysis_dir / "language_uniformity-test_z_FDR_0.01.nii.gz"
    location_assoc = coactivation_dir / "metaanalytic_coactivation_0_14_42_association-test_z_FDR_0.01.nii.gz"
    location_fc = coactivation_dir / "functional_connectivity_0_14_42.nii.gz"
    uploaded_image = decoded_dir / "uploaded_test_image.nii.gz"

    for path in [language_assoc, language_uniform, location_assoc, location_fc, uploaded_image]:
        _write_dummy_nifti(path)

    analysis_set = AnalysisSet(
        name="abstract terms",
        type="terms",
        description="Dummy analyses for tests",
        n_analyses=5,
    )
    database.session.add(analysis_set)

    analyses = {}
    for name in ["reward", "language", "emotion", "pain", "working memory"]:
        analyses[name] = TermAnalysis(
            analysis_set=analysis_set,
            name=name,
            description=f"{name} analysis",
            n_studies=2,
            n_activations=3,
            display=True,
        )
        database.session.add(analyses[name])

    language_image_1 = TermAnalysisImage(
        analysis=analyses["language"],
        name="Language association",
        label="language: association test",
        description="Dummy language association image",
        stat="z-score",
        image_file=str(language_assoc),
        display=True,
        download=True,
    )
    language_image_2 = TermAnalysisImage(
        analysis=analyses["language"],
        name="Language uniformity",
        label="language: uniformity test",
        description="Dummy language uniformity image",
        stat="z-score",
        image_file=str(language_uniform),
        display=True,
        download=True,
    )
    database.session.add_all([language_image_1, language_image_2])

    location = Location(0, 14, 42)
    location.images.extend(
        [
            LocationImage(
                name="Meta-analytic coactivation",
                label="Meta-analytic coactivation",
                description="Dummy coactivation image",
                stat="z-score",
                image_file=str(location_assoc),
                display=True,
                download=True,
            ),
            LocationImage(
                name="Functional connectivity",
                label="Functional connectivity",
                description="Dummy functional connectivity image",
                stat="corr. (r)",
                image_file=str(location_fc),
                display=True,
                download=True,
            ),
        ]
    )
    database.session.add(location)

    study_1 = Study(
        pmid=1001,
        title="Language Study One",
        authors="Example A",
        journal="Journal A",
        year=2020,
    )
    study_2 = Study(
        pmid=1002,
        title="Language Study Two",
        authors="Example B",
        journal="Journal B",
        year=2021,
    )
    study_3 = Study(
        pmid=1003,
        title="Language Study Three",
        authors="Example C",
        journal="Journal C",
        year=2022,
    )
    database.session.add_all([study_1, study_2, study_3])

    database.session.add_all(
        [
            Peak(pmid=1001, table="1", x=0, y=14, z=42),
            Peak(pmid=1001, table="1", x=2, y=14, z=42),
            Peak(pmid=1002, table="1", x=0, y=16, z=42),
            Peak(pmid=1003, table="1", x=0, y=24, z=42),
        ]
    )
    database.session.add_all(
        [
            Frequency(analysis=analyses["language"], study=study_1, frequency=0.9),
            Frequency(analysis=analyses["language"], study=study_2, frequency=0.8),
            Frequency(analysis=analyses["reward"], study=study_3, frequency=0.7),
        ]
    )

    decoding_set = DecodingSet(
        name="terms_20k",
        n_images=2,
        n_voxels=10,
        is_subsampled=True,
    )
    database.session.add(decoding_set)
    database.session.flush()

    decoding = Decoding(
        uuid="dummydecodeuuid0000000000000001",
        filename=str(uploaded_image),
        name="Dummy uploaded image",
        display=True,
        download=False,
        decoding_set=decoding_set,
        image=language_image_1,
    )
    database.session.add(decoding)
    database.session.flush()

    (decoding_results_dir / f"{decoding.uuid}.txt").write_text(
        "reward\t0.812\nlanguage\t0.456\n",
        encoding="utf-8",
    )

    database.session.commit()
    return {
        "analysis_id": analyses["language"].id,
        "image_id": language_image_1.id,
        "location": (0, 14, 42),
        "decode_uuid": decoding.uuid,
    }


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    root = tmp_path_factory.mktemp("nsweb-tests")
    _configure_test_settings(root)

    from nsweb.core import app as flask_app
    from nsweb.core import create_app

    create_app(debug=True, test=True)
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def db(app):
    from nsweb.core import cache
    from nsweb.core import db as database

    with app.app_context():
        cache.clear()
        database.session.remove()
        database.drop_all()
        database.create_all()
        yield database
        database.session.remove()
        cache.clear()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def dummy_data(app, db, tmp_path_factory):
    with app.app_context():
        return _seed_dummy_data(db, Path(settings.DATA_DIR).parent)
