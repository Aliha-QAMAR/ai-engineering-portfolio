import os
import pandas as pd
import matplotlib.pyplot as plt

def get_schema(df: pd.DataFrame) -> dict:
    return {
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "total_rows": len(df)
    }

def profile_dataset(df: pd.DataFrame) -> dict:
    return {
        "shape": list(df.shape),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_summary": df.describe().to_dict()
    }

def describe_column(df: pd.DataFrame, column: str) -> dict:
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    series = df[column]
    res = {
        "dtype": str(series.dtype),
        "null_count": int(series.isnull().sum()),
        "unique_values": int(series.nunique())
    }
    
    if pd.api.types.is_numeric_dtype(series):
        res.update({
            "min": float(series.min()) if not pd.isna(series.min()) else None,
            "max": float(series.max()) if not pd.isna(series.max()) else None,
            "mean": float(series.mean()) if not pd.isna(series.mean()) else None,
            "median": float(series.median()) if not pd.isna(series.median()) else None
        })
    else:
        res["top_values"] = series.value_counts().head(5).to_dict()
        
    return res

def filter_rows(df: pd.DataFrame, column: str, operator: str, value) -> dict:
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    ops = {
        "==": df[column] == value,
        "!=": df[column] != value,
        ">": df[column] > value,
        "<": df[column] < value,
        ">=": df[column] >= value,
        "<=": df[column] <= value
    }
    
    if operator not in ops:
        return {"error": f"Unsupported operator '{operator}'"}
        
    filtered = df[ops[operator]]
    return {
        "matching_rows": len(filtered),
        "sample": filtered.head(10).to_dict(orient="records")
    }

def group_and_aggregate(df: pd.DataFrame, group_by: str, metric: str, operation: str) -> dict:
    if group_by not in df.columns or metric not in df.columns:
        return {"error": "Invalid column specified"}
        
    valid_ops = ["sum", "mean", "count", "min", "max"]
    if operation not in valid_ops:
        return {"error": f"Invalid operation. Choose from {valid_ops}"}
        
    res = df.groupby(group_by)[metric].agg(operation).reset_index()
    return res.to_dict(orient="records")

def top_n(df: pd.DataFrame, column: str, n: int = 5, ascending: bool = False) -> dict:
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    sorted_df = df.sort_values(by=column, ascending=ascending).head(n)
    return sorted_df.to_dict(orient="records")

def compare_periods(df: pd.DataFrame, date_column: str, metric: str, period_a: str, period_b: str) -> dict:
    if date_column not in df.columns or metric not in df.columns:
        return {"error": "Invalid date or metric column"}
        
    df[date_column] = pd.to_datetime(df[date_column])
    val_a = df[df[date_column] == period_a][metric].sum()
    val_b = df[df[date_column] == period_b][metric].sum()
    
    diff = val_b - val_a
    pct_change = (diff / val_a * 100) if val_a != 0 else 0
    
    return {
        "period_a": period_a,
        "value_a": float(val_a),
        "period_b": period_b,
        "value_b": float(val_b),
        "difference": float(diff),
        "pct_change": float(pct_change)
    }

def make_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str = "Chart") -> dict:
    if x_col not in df.columns or y_col not in df.columns:
        return {"error": "Columns specified for chart do not exist"}
        
    os.makedirs("results/charts", exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    if chart_type == "bar":
        ax.bar(df[x_col].astype(str), df[y_col])
    elif chart_type == "line":
        ax.plot(df[x_col], df[y_col], marker="o")
    elif chart_type == "scatter":
        ax.scatter(df[x_col], df[y_col])
    else:
        plt.close(fig)
        return {"error": "Chart type must be bar, line, or scatter"}
        
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filename = f"results/charts/{title.lower().replace(' ', '_')}.png"
    plt.savefig(filename)
    plt.close(fig)
    
    return {"status": "success", "file_path": filename}  #end here 
