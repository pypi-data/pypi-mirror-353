from __future__ import annotations
from typing import Type, List, Any, Dict
from pydantic import BaseModel, model_validator
from .base_factory import ContractFactoryBase
from .feature_factory import PydanticFeatureFactory
from .encoders import NaInfEncoder


class PydanticRequestFactory(ContractFactoryBase):
    """
    Строит Dto-класс PredictRequest с полями для REST API
    клиента модели (mlflow serve).

    Формат запроса, который по умолчанию понимимает Mlflow Serve имеет
    вид:
    ```json
    {
        "dataframe_split": {
            "columns": [...],
            "data": [[...], ...]
        }
    }
    ```
    """

    def __init__(self, *args, feature_cls: Type[BaseModel], **kw) -> None:
        super().__init__(*args, **kw)
        self.feature_cls = feature_cls
        self._cols = list(self.inputs)

    def build(self) -> Type[BaseModel]:
        cols = self._cols
        enc  = self.encoder
        FeatureRow = self.feature_cls

        class PredictRequest(BaseModel):
            rows: List[FeatureRow]
            model_config = {"json_encoders": {float: enc}}

            @model_validator(mode="after")
            def _no_empty(self):
                if not self.rows:
                    raise ValueError("rows can't be empty")
                return self

            def to_split_json(
                self, *, encoder: NaInfEncoder | None = None
            ) -> Dict[str, Any]:
                e = encoder or enc
                data = [[e(getattr(r, c)) for c in cols] for r in self.rows]
                return {"dataframe_split": {"columns": cols, "data": data}}

        PredictRequest.__name__ = f"{self.prefix}_PredictRequest"
        return PredictRequest
