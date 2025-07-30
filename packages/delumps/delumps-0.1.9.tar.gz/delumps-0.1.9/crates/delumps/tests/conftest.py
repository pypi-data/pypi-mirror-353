import os
import typing

import pytest

from model import Sample, PhenotypicFeature


@pytest.fixture(scope="session")
def fpath_project_dir() -> str:
    return os.getcwd()


@pytest.fixture(scope="session")
def fpath_resources_dir(
    fpath_project_dir: str,
) -> str:
    return os.path.join(
        fpath_project_dir,
        "crates",
        "scone",
        "resources",
    )


@pytest.fixture(scope="session")
def fpath_hpo(
    fpath_resources_dir: str,
) -> str:
    return os.path.join(fpath_resources_dir, "hp.v2024-04-26.json.gz")


@pytest.fixture(scope="session")
def fpath_ic_mica_dict(
    fpath_resources_dir: str,
) -> str:
    return os.path.join(
        fpath_resources_dir,
        "term-pair-similarity.2023-10-09.FBN1.csv.gz",
    )


@pytest.fixture(scope="session")
def example_samples() -> typing.Sequence[Sample]:
    return (
        Sample(
            # labels=SampleLabels(label="B1", meta_label="PMID_12203992_B1"),
            phenotypic_features=make_features(
                [
                    ("HP:0000268", True),
                    ("HP:0001763", True),
                    ("HP:0001166", True),
                    ("HP:0000218", True),
                    ("HP:0001519", True),
                    ("HP:0001377", True),
                    ("HP:0001083", True),
                    ("HP:0000545", True),
                    ("HP:0002616", True),
                    ("HP:0001634", True),
                ]
            ),
        ),
        Sample(
            # labels=SampleLabels(label="B3", meta_label="PMID_12203992_B3"),
            phenotypic_features=make_features(
                [
                    ("HP:0001166", True),
                    ("HP:0000098", True),
                    ("HP:0002650", True),
                    ("HP:0001083", True),
                    ("HP:0000545", True),
                    ("HP:0002616", True),
                ]
            ),
        ),
        Sample(
            # labels=SampleLabels(label="B9", meta_label="PMID_12203992_B9"),
            phenotypic_features=make_features(
                [
                    ("HP:0001166", True),
                    ("HP:0001763", True),
                    ("HP:0000098", True),
                    ("HP:0000767", True),
                    ("HP:0001083", True),
                    ("HP:0002616", True),
                ]
            ),
        ),
        Sample(
            # labels=SampleLabels(label="BM", meta_label="PMID_12446365_BM"),
            phenotypic_features=make_features(
                [
                    ("HP:0001083", True),
                    ("HP:0001065", True),
                    ("HP:0012773", True),
                    ("HP:0000501", False),
                    ("HP:0000545", False),
                    ("HP:0000486", False),
                    ("HP:0002650", False),
                    ("HP:0001382", False),
                    ("HP:0000767", False),
                    ("HP:0001166", False),
                    ("HP:0000541", False),
                    ("HP:0000768", False),
                    ("HP:0000218", False),
                    ("HP:0002616", False),
                    ("HP:0001634", False),
                ]
            ),
        ),
        Sample(
            # labels=SampleLabels(label="JL", meta_label="PMID_12446365_JL"),
            phenotypic_features=make_features(
                [
                    ("HP:0001083", True),
                    ("HP:0000545", True),
                    ("HP:0001382", True),
                    ("HP:0000768", True),
                    ("HP:0000218", True),
                    ("HP:0001065", True),
                    ("HP:0000501", False),
                    ("HP:0000486", False),
                    ("HP:0002650", False),
                    ("HP:0000767", False),
                    ("HP:0001166", False),
                    ("HP:0000541", False),
                    ("HP:0002616", False),
                    ("HP:0001634", False),
                    ("HP:0012773", False),
                ]
            ),
        ),
        Sample(
            # labels=SampleLabels(label="OP", meta_label="PMID_12446365_OP"),
            phenotypic_features=make_features(
                [
                    ("HP:0001083", True),
                    ("HP:0000545", True),
                    ("HP:0001166", True),
                    ("HP:0000218", True),
                    ("HP:0001634", True),
                    ("HP:0012773", True),
                    ("HP:0000501", False),
                    ("HP:0000486", False),
                    ("HP:0002650", False),
                    ("HP:0001382", False),
                    ("HP:0000767", False),
                    ("HP:0000541", False),
                    ("HP:0000768", False),
                    ("HP:0001065", False),
                    ("HP:0002616", False),
                ]
            ),
        ),
    )


def make_features(
    features: typing.Iterable[typing.Tuple[str, bool]],
) -> typing.Iterable[PhenotypicFeature]:
    vals = []
    for feature in features:
        pf = PhenotypicFeature(feature[0], is_present=feature[1])
        vals.append(pf)
    return vals
