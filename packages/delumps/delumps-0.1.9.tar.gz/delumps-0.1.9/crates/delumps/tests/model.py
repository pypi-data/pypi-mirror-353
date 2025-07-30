import typing


class PhenotypicFeature:
    def __init__(
        self,
        term_id: str,
        is_present: bool,
    ):
        self._term_id = term_id
        self._is_present = is_present

    @property
    def identifier(self) -> str:
        return self._term_id

    @property
    def is_present(self) -> bool:
        return self._is_present


class Sample:
    """
    The bare-bones `Sample` implementation.
    """

    def __init__(
        self,
        phenotypic_features: typing.Iterable[PhenotypicFeature],
    ):
        self._pfs = tuple(phenotypic_features)

    @property
    def phenotypic_features(self) -> typing.Sequence[PhenotypicFeature]:
        return self._pfs
