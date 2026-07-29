import json
import asyncio
import pandas as pd
from tools import get_schema, group_and_aggregate, make_chart

GLOBAL_DF = pd.DataFrame({
    "date": ["2024-01-01", "2024-01-01", "2024-02-01", "2024-02-01"],
    "product": ["A", "B", "A", "B"],
    "revenue": [100, 200, 150, 400]
})

class MCPServer:
    def __init__(self):
        self.tools = {
            "get_schema": self.handle_get_schema,
            "group_and_aggregate": self.handle_group_and_aggregate,
            "make_chart": self.handle_make_chart
        }
        self.resources = {
            "resource://dataset/metadata": self.handle_dataset_metadata
        }

    def handle_get_schema(self, args):
        return get_schema(GLOBAL_DF)

    def handle_group_and_aggregate(self, args):
        return group_and_aggregate(GLOBAL_DF, **args)

    def handle_make_chart(self, args):
        return make_chart(GLOBAL_DF, **args)

    def handle_dataset_metadata(self):
        return {
            "uri": "resource://dataset/metadata",
            "mimeType": "application/json",
            "content": {
                "rows": len(GLOBAL_DF),
                "columns": list(GLOBAL_DF.columns),
                "description": "Sales and revenue metrics by product and date."
            }
        }

    def list_tools(self):
        return [
            {"name": "get_schema", "description": "Get dataset column names and data types"},
            {"name": "group_and_aggregate", "description": "Group data and compute aggregate metrics"},
            {"name": "make_chart", "description": "Generate charts for data visualization"}
        ]

    async def process_request(self, json_rpc_req: str):
        try:
            req = json.loads(json_rpc_req)
            method = req.get("method")
            req_id = req.get("id")

            if method == "tools/list":
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.list_tools()}})
            
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                if name in self.tools:
                    result = self.tools[name](args)
                    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}})
                else:
                    return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Tool not found"}})

            elif method == "resources/read":
                uri = req.get("params", {}).get("uri")
                if uri in self.resources:
                    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": self.resources[uri]()})

        except Exception as e:
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    server = MCPServer()
    print("🚀 MCP Server Running. Listening for JSON-RPC requests...")
    
    sample_request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    response = asyncio.run(server.process_request(sample_request))
    print("\nClient Request: tools/list")
    print("MCP Server Response:\n", json.dumps(json.loads(response), indent=2))
