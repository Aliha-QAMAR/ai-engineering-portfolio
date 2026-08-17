from backend.tool_schemas import TOOL_SCHEMAS
from backend.tools import (analyze_csv, analyze_document, analyze_image, search_evidence, 
                          build_timeline, map_relationships, calculate_statistics, consult_previous_cases)

class MCPServer:
    def __init__(self):
        self.tools = {}
        self.register_default_tools()
        
    def register_default_tools(self):
        tools_map = {
            "analyze_csv": analyze_csv,
            "analyze_document": analyze_document,
            "analyze_image": analyze_image,
            "search_evidence": search_evidence,
            "build_timeline": build_timeline,
            "map_relationships": map_relationships,
            "calculate_statistics": calculate_statistics,
            "consult_previous_cases": consult_previous_cases
        }
        for schema in TOOL_SCHEMAS:
            name = schema["function"]["name"]
            if name in tools_map:
                self.register_tool(name, schema["function"], tools_map[name])
                
    def register_tool(self, name, schema, func):
        self.tools[name] = {"schema": schema, "func": func}
        
    def list_tools(self):
        return [tool["schema"] for tool in self.tools.values()]
        
    def call_tool(self, name, arguments):
        if name in self.tools:
            return self.tools[name]["func"](**arguments)
        raise ValueError(f"Tool {name} not found")
