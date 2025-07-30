import typing

import pytest
import delumps
import numpy as np

from model import Sample


class TestSimilarityMatrixCreatorFactory:
    @pytest.fixture(
        scope="class",
    )
    def similarity_matrix_creator_factory(
        self,
        fpath_hpo: str,
        fpath_ic_mica_dict: str,
    ) -> delumps.SimilarityMatrixCreatorFactory:
        return delumps.SimilarityMatrixCreatorFactory.from_hpo_and_ic_mica(
            fpath_hpo,
            fpath_ic_mica_dict,
        )

    def test_phenomizer_calculate_matrix(
        self,
        similarity_matrix_creator_factory: delumps.SimilarityMatrixCreatorFactory,
        example_samples: typing.Sequence[Sample],
    ):
        smc = similarity_matrix_creator_factory.create_phenomizer_smc()
        sm = smc.calculate_matrix(example_samples)  # type: ignore <- this is False Positive

        assert hasattr(sm, "similarity_matrix"), (
            "SimilarityMatrix should have `similarity_matrix` attribute to interoperate with Python"
        )

        sm = sm.similarity_matrix

        assert isinstance(sm, np.ndarray), "We better get a Numpy array"
        assert sm.shape == (
            len(example_samples),
            len(example_samples),
        ), "The array must be square"
        assert (sm > 0.0).all(), "All similarities must be non-negative"

        assert np.allclose(
            sm,
            np.array(
                [
                    [
                        4.31987721,
                        3.25954348,
                        3.31252243,
                        1.53677505,
                        1.84277567,
                        3.07855208,
                    ],
                    [
                        3.25954348,
                        4.03559044,
                        3.46397316,
                        1.79345385,
                        1.65511032,
                        2.68767014,
                    ],
                    [
                        3.31252243,
                        3.46397316,
                        4.32659789,
                        1.72763528,
                        1.54255577,
                        2.31170788,
                    ],
                    [
                        1.53677505,
                        1.79345385,
                        1.72763528,
                        6.82491476,
                        2.82697507,
                        3.72970455,
                    ],
                    [
                        1.84277567,
                        1.65511032,
                        1.54255577,
                        2.82697507,
                        4.03211492,
                        1.98232776,
                    ],
                    [
                        3.07855208,
                        2.68767014,
                        2.31170788,
                        3.72970455,
                        1.98232776,
                        4.86140862,
                    ],
                ]
            ),
        )

    def test_create_scone_smc_with_default_parameters(
        self,
        similarity_matrix_creator_factory: delumps.SimilarityMatrixCreatorFactory,
    ):
        """
        Test creating similarity matrix creator with default parameters
        """
        smc = similarity_matrix_creator_factory.create_scone_smc()

        self._test_smc_attributes(smc)

    @pytest.mark.parametrize(
        "strategy,skip_matching_excluded_features",
        [
            (delumps.ExcludedAncestorStrategy.Penalize, True),
            (delumps.ExcludedAncestorStrategy.Skip, True),
            (delumps.ExcludedAncestorStrategy.Penalize, False),
            (delumps.ExcludedAncestorStrategy.Skip, False),
        ],
    )
    def test_create_scone_smc_parametrized(
        self,
        similarity_matrix_creator_factory: delumps.SimilarityMatrixCreatorFactory,
        strategy: delumps.ExcludedAncestorStrategy,
        skip_matching_excluded_features: bool,
    ):
        smc = similarity_matrix_creator_factory.create_scone_smc(
            excluded_ancestor_strategy=strategy,
            skip_matching_excluded_features=skip_matching_excluded_features,
        )

        self._test_smc_attributes(smc)

    def _test_smc_attributes(
        self,
        smc: delumps.SimilarityMatrixCreator,
    ):
        assert hasattr(smc, "calculate_matrix") and callable(smc.calculate_matrix)

    def test_calculate_matrix(
        self,
        similarity_matrix_creator_factory: delumps.SimilarityMatrixCreatorFactory,
        example_samples: typing.Sequence[Sample],
    ):
        seq_smc = similarity_matrix_creator_factory.create_scone_smc(
            delumps.ExcludedAncestorStrategy.Skip, False
        )
        sm = seq_smc.calculate_matrix(example_samples)  # type: ignore <- this is False Positive

        assert hasattr(sm, "similarity_matrix"), (
            "SimilarityMatrix should have `similarity_matrix` attribute to interoperate with Python"
        )

        a = sm.similarity_matrix

        assert isinstance(a, np.ndarray), "We better get a Numpy array"
        assert a.shape == (
            len(example_samples),
            len(example_samples),
        ), "The array must be square"
        assert (a > 0.0).all(), "All similarities must be non-negative"
