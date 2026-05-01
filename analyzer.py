import pandas as pd


def analyze_data(df: pd.DataFrame) -> dict:
    """Returns a summary dictionary of the dataframe."""
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    summary = {
        "shape": df.shape,
        "total_missing": int(df.isnull().sum().sum()),
        "missing_pct": round(
            df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2
        ),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "duplicate_rows": int(df.duplicated().sum()),
    }

    if numeric_cols:
        summary["stats"] = df[numeric_cols].describe().round(2).to_dict()

    return summary


def get_data_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a detailed per-column profile as a DataFrame."""
    profile = []
    for col in df.columns:
        col_data = df[col]
        dtype = str(col_data.dtype)
        missing = int(col_data.isnull().sum())
        missing_pct = round(missing / len(df) * 100, 1)
        unique = int(col_data.nunique())

        row = {
            "Column": col,
            "Data Type": dtype,
            "Missing": missing,
            "Missing %": f"{missing_pct}%",
            "Unique Values": unique,
        }

        if col_data.dtype in ['int64', 'float64']:
            row["Min"] = round(col_data.min(), 2)
            row["Max"] = round(col_data.max(), 2)
            row["Mean"] = round(col_data.mean(), 2)
            row["Std Dev"] = round(col_data.std(), 2)
            row["Top Value"] = "-"
        else:
            row["Min"] = "-"
            row["Max"] = "-"
            row["Mean"] = "-"
            row["Std Dev"] = "-"
            row["Top Value"] = (
                col_data.mode()[0] if not col_data.mode().empty else "-"
            )

        profile.append(row)

    return pd.DataFrame(profile)