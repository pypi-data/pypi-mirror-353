"""Calculate players features."""

# pylint: disable=too-many-locals,too-many-branches,too-many-statements
import statistics
from warnings import simplefilter

import pandas as pd
import tqdm
from scipy.stats import kurtosis, sem, skew  # type: ignore

from .columns import DELIMITER
from .identifier import Identifier

PLAYERS_COLUMN = "players"


def players_process(df: pd.DataFrame, identifiers: list[Identifier]) -> pd.DataFrame:
    """Process players stats on a team."""
    simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
    df_dict: dict[str, list[float | None]] = {}
    df_cols = df.columns.values.tolist()

    team_identifiers: dict[str, list[Identifier]] = {}
    for identifier in identifiers:
        if identifier.team_identifier_column is None:
            continue
        team_identifier = [
            x for x in identifiers if x.column == identifier.team_identifier_column
        ]
        team_identifiers[team_identifier[0].column_prefix] = team_identifiers.get(
            team_identifier[0].column_prefix, []
        ) + [identifier]

    written_columns = set()
    for row in tqdm.tqdm(
        df.itertuples(name=None), desc="Players Processing", total=len(df)
    ):
        row_dict = {x: row[count + 1] for count, x in enumerate(df_cols)}

        for column_prefix, player_identifiers in team_identifiers.items():
            columns: dict[str, list[float]] = {}

            for identifier in player_identifiers:
                for key, value in row_dict.items():
                    if not key.startswith(identifier.column_prefix):
                        continue
                    if not isinstance(value, float):
                        continue
                    column = key[len(identifier.column_prefix) :]
                    columns[column] = columns.get(column, []) + [value]

            for column, values in columns.items():
                if not values:
                    continue
                mean_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "mean"]
                )
                if mean_column not in df_dict:
                    df_dict[mean_column] = [None for _ in range(len(df))]
                df_dict[mean_column][row[0]] = statistics.mean(values)
                written_columns.add(mean_column)

                median_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "median"]
                )
                if median_column not in df_dict:
                    df_dict[median_column] = [None for _ in range(len(df))]
                df_dict[median_column][row[0]] = statistics.median(values)
                written_columns.add(median_column)

                min_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "min"]
                )
                if min_column not in df_dict:
                    df_dict[min_column] = [None for _ in range(len(df))]
                df_dict[min_column][row[0]] = min(values)
                written_columns.add(min_column)

                max_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "max"]
                )
                if max_column not in df_dict:
                    df_dict[max_column] = [None for _ in range(len(df))]
                df_dict[max_column][row[0]] = max(values)
                written_columns.add(max_column)

                count_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "count"]
                )
                if count_column not in df_dict:
                    df_dict[count_column] = [None for _ in range(len(df))]
                df_dict[count_column][row[0]] = float(len(values))
                written_columns.add(count_column)

                sum_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "sum"]
                )
                if sum_column not in df_dict:
                    df_dict[sum_column] = [None for _ in range(len(df))]
                df_dict[sum_column][row[0]] = sum(values)
                written_columns.add(sum_column)

                var_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "var"]
                )
                if var_column not in df_dict:
                    df_dict[var_column] = [None for _ in range(len(df))]
                df_dict[var_column][row[0]] = statistics.variance(values)
                written_columns.add(var_column)

                std_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "std"]
                )
                if std_column not in df_dict:
                    df_dict[std_column] = [None for _ in range(len(df))]
                df_dict[std_column][row[0]] = statistics.stdev(values)
                written_columns.add(std_column)

                skew_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "skew"]
                )
                if skew_column not in df_dict:
                    df_dict[skew_column] = [None for _ in range(len(df))]
                df_dict[skew_column][row[0]] = skew(values)
                written_columns.add(skew_column)

                kurt_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "kurt"]
                )
                if kurt_column not in df_dict:
                    df_dict[kurt_column] = [None for _ in range(len(df))]
                df_dict[kurt_column][row[0]] = kurtosis(values)
                written_columns.add(kurt_column)

                sem_column = DELIMITER.join(
                    [column_prefix, PLAYERS_COLUMN, column, "sem"]
                )
                if sem_column not in df_dict:
                    df_dict[sem_column] = [None for _ in range(len(df))]
                df_dict[sem_column][row[0]] = sem(values)
                written_columns.add(sem_column)

    for column in written_columns:
        df.loc[:, column] = df_dict[column]

    return df[sorted(df.columns.values.tolist())].copy()
