"""OpenAI tool schemas. The model may only *request* these; the agent
validates every call (allowed tool + allowed evidence file) before executing.
"""

def _file(desc="Evidence file name to analyze (as shown on the evidence board)"):
    return {"type": "string", "description": desc}


TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_schema",
        "description": "Inspect a CSV evidence file: detected columns, data types, and record count.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file()},
                       "required": ["file_path"]}}},
    {"type": "function", "function": {
        "name": "profile_dataset",
        "description": "Deep profile of a CSV: record count, duplicate rows, duplicate identifiers "
                       "(e.g. an invoice number paid twice), null counts, numeric summaries and date columns.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file()},
                       "required": ["file_path"]}}},
    {"type": "function", "function": {
        "name": "describe_column",
        "description": "Statistics for a single column: type, unique count, top values or numeric range.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file(), "column": {"type": "string"}},
                       "required": ["file_path", "column"]}}},
    {"type": "function", "function": {
        "name": "filter_rows",
        "description": "Return rows matching a condition. op is one of eq, ne, gt, lt, gte, lte, contains.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file(), "column": {"type": "string"},
                                      "op": {"type": "string",
                                             "enum": ["eq", "ne", "gt", "lt", "gte", "lte", "contains"]},
                                      "value": {"type": "string"}},
                       "required": ["file_path", "column", "op", "value"]}}},
    {"type": "function", "function": {
        "name": "group_and_aggregate",
        "description": "Group a CSV by a column and aggregate another (count, sum, mean, min, max). "
                       "Use count on an identifier column to surface duplicates.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file(), "group_by": {"type": "string"},
                                      "agg_column": {"type": "string"},
                                      "agg": {"type": "string",
                                              "enum": ["count", "sum", "mean", "min", "max"]}},
                       "required": ["file_path", "group_by"]}}},
    {"type": "function", "function": {
        "name": "top_n",
        "description": "Top N values of a column, or top N groups by an aggregated measure.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file(), "column": {"type": "string"},
                                      "n": {"type": "integer"}, "by": {"type": "string"},
                                      "agg": {"type": "string"}},
                       "required": ["file_path", "column"]}}},
    {"type": "function", "function": {
        "name": "compare_periods",
        "description": "Bucket a value column by month using a date column; returns per-period totals "
                       "and the percentage change of the latest period.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file(), "date_column": {"type": "string"},
                                      "value_column": {"type": "string"}},
                       "required": ["file_path", "date_column", "value_column"]}}},
    {"type": "function", "function": {
        "name": "build_timeline",
        "description": "Extract a chronological, sorted timeline of events from a CSV's date column.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file()},
                       "required": ["file_path"]}}},
    {"type": "function", "function": {
        "name": "map_relationships",
        "description": "Build a relationship graph (nodes + edges) from identifier columns of a CSV "
                       "such as vendor, account, invoice, email, person.",
        "parameters": {"type": "object",
                       "properties": {"file_path": _file()},
                       "required": ["file_path"]}}},
    {"type": "function", "function": {
        "name": "consult_previous_cases",
        "description": "Search NOCTRA's long-term memory for similar past investigations.",
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string"}},
                       "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "make_chart",
        "description": "Produce a chart spec (bar, line or pie) from labels and values for the report.",
        "parameters": {"type": "object",
                       "properties": {"chart_type": {"type": "string", "enum": ["bar", "line", "pie"]},
                                      "labels": {"type": "array", "items": {"type": "string"}},
                                      "values": {"type": "array", "items": {"type": "number"}},
                                      "title": {"type": "string"}},
                       "required": ["chart_type", "labels", "values"]}}},
]
