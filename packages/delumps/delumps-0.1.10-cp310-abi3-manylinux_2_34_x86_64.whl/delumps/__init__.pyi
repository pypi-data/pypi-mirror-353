import typing

import numpy as np
import numpy.typing as npt

class ExcludedAncestorStrategy:
    """
    Strategy for resolving a conflict between a present HPO term
    (e.g. *Clonic seizure*) in subject *A*
    and its excluded ancestor (e.g. no *Seizure*) in subject *B*.
    """

    Skip: ExcludedAncestorStrategy
    """
    No explicit penalty. However, the excluded `ancestor`
    will contribute nothing to the match.
    """

    Penalize: ExcludedAncestorStrategy
    """
    Apply a simple penalty: consider the excluded `ancestor`
    as a mismatch using the negated IC of the excluded ancestor.
    """

class PhenotypicFeature(typing.Protocol):
    """
    Represents a phenotypic feature (an HPO term)
    that can be present or excluded.
    """
    @property
    def curie(self) -> str:
        """
        Get the CURIE string of the HPO term (e.g. `HP:0001250` for *Seizure*).
        """
        ...

    @property
    def is_present(self) -> bool:
        """
        Return `True` if the phenotypic feature was observed/present in the indiviudal,
        and `False` otherwise.
        """
        ...

class Sample(typing.Protocol):
    """
    Represents an individual with phenotype information.
    """

    @property
    def phenotypic_features(self) -> typing.Iterable[PhenotypicFeature]:
        """
        Get the phenotypic features of the individual.
        """
        ...

class SimilarityMatrix:
    """
    `SimilarityMatrix` has a 2D square symmetric matrix with semantic similarities.
    """

    @property
    def similarity_matrix(self) -> npt.NDArray[np.float64]:
        """
        Get the similarity matrix.
        """
        ...

class SimilarityMatrixCreator:
    """
    Similarity matrix creator computes a similarity matrix for given samples.
    """

    def calculate_matrix(
        self,
        samples: typing.Sequence[Sample],
    ) -> SimilarityMatrix:
        """
        Compute similarity matrix for given `samples`.
        """
        ...

class SimilarityMatrixCreatorFactory:
    """
    Creates similarity matrix creators in various configurations.
    """

    @staticmethod
    def from_hpo_and_ic_mica(
        fpath_hpo: str,
        fpath_ic_mica: str,
    ) -> SimilarityMatrixCreatorFactory:
        """
        The static constructor of the factory.

        We need paths to HPO JSON file and to the table with IC MICA values.

        Deprecated: use the constructor instead.
        """
        ...

    def __init__(
        self,
        fpath_hpo: str,
        fpath_ic_mica: str,
    ) -> None:
        """
        Create the factory from the HPO JSON file and to the table with IC MICA values.
        """
        ...

    def create_phenomizer_smc(self) -> SimilarityMatrixCreator:
        """
        Create similarity matrix creator that uses Phenomizer under the hood.
        """
        ...

    def create_scone_smc(
        self,
        excluded_ancestor_strategy: ExcludedAncestorStrategy = ExcludedAncestorStrategy.Skip,
        skip_matching_excluded_features: bool = False,
    ) -> SimilarityMatrixCreator:
        """
        Create similarity matrix creator that uses Scone under the hood.
        """
        ...
