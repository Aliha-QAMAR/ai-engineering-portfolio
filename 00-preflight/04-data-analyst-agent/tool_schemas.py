TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_schema",
            "description": "Returns dataset columns and data types.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {  
        "type": "function",
        "function": {
            "name": "profile_dataset",
            "description": "Returns full summary, shape, missing values, and describe block.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_column",
            "description": "Detailed summary statistics for a specific column.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"}
                },
                "required": ["column"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_rows",
            "description": "Filter rows matching a basic conditional rule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "operator": {"type": "string", "enum": ["==", "!=", ">", "<", ">=", "<="]},
                    "value": {"type": ["string", "number"]}
                },
                "required": ["column", "operator", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "group_and_aggregate",
            "description": "Groups dataset by column and applies aggregation operation on metric.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {"type": "string"},
                    "metric": {"type": "string"},
                    "operation": {"type": "string", "enum": ["sum", "mean", "count", "min", "max"]}
                },
                "required": ["group_by", "metric", "operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "top_n",
            "description": "Retrieve top or bottom N rows ordered by a metric.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "n": {"type": "integer", "default": 5},
                    "ascending": {"type": "boolean", "default": False}
                },
                "required": ["column"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_periods",
            "description": "Compares aggregated metric across two specific periods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_column": {"type": "string"},
                    "metric": {"type": "string"},
                    "period_a": {"type": "string"},
                    "period_b": {"type": "string"}
                },
                "required": ["date_column", "metric", "period_a", "period_b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_chart",
            "description": "Generates a chart and saves it locally.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {"type": "string", "enum": ["bar", "line", "scatter"]},
                    "x_col": {"type": "string"},
                    "y_col": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["chart_type", "x_col", "y_col"]
            }
        }
    }
]
