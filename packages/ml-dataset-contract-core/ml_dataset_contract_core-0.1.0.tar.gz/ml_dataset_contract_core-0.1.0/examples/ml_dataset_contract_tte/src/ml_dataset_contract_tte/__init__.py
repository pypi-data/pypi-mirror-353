from importlib.resources import files

from ml_dataset_contract.runtime import (
    PydanticFeatureFactory,
    PydanticTargetFactory,
    PydanticRequestFactory,
)

_YAML = files(__name__).joinpath("dataset.yml")

TteFeatureRow = PydanticFeatureFactory(_YAML, prefix="Tte").build()
TteTargetRow  = PydanticTargetFactory(_YAML, prefix="Tte").build()
TtePredictRequest = PydanticRequestFactory(
    _YAML, prefix="Tte", feature_cls=TteFeatureRow
).build()

__all__ = [
    "TteFeatureRow", "TteTargetRow", "TtePredictRequest", "_YAML"
]