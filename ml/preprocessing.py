import pandas as pd

from ml.features import FEATURE_COLUMNS


def prepare_features(feature_dict):

    data = {}

    for column in FEATURE_COLUMNS:

        value = feature_dict.get(
            column,
            0
        )

        try:
            data[column] = float(value)

        except (
            TypeError,
            ValueError
        ):
            data[column] = 0.0

    dataframe = pd.DataFrame(
        [data],
        columns=FEATURE_COLUMNS
    )

    return dataframe