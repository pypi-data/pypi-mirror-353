from ml_dataset_contract_tte import (
    TteFeatureRow,
    TteTargetRow,
    TtePredictRequest,
)


sample_row__input = {
    "expanding_tte_mean": 1.1,
    "tte_lag_1": 1.2,
}
sample_row__target = {"tte": 1.3}

feature_row = TteFeatureRow(**sample_row__input)
print(f"{feature_row=}")

target_row = TteTargetRow(**sample_row__target)
print(f"{target_row=}")

request = TtePredictRequest(rows=[feature_row])
payload = request.to_split_json()
print(f"{payload}")
