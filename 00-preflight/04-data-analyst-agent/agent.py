import json
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tools import (
    get_schema, profile_dataset, describe_column, filter_rows,
    group_and_aggregate, top_n, compare_periods, make_chart
)
from tool_schemas import TOOLS_SCHEMA

load_dotenv()

class DataAnalystAgent:
    def __init__(self, df: pd.DataFrame, model: str = "llama-3.1-8b-instant"):
        self.df = df
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = model
        self.max_steps = 8
        self.tools_map = {
            "get_schema": lambda **kw: get_schema(self.df, **kw),
            "profile_dataset": lambda **kw: profile_dataset(self.df, **kw),
            "describe_column": lambda **kw: describe_column(self.df, **kw),
            "filter_rows": lambda **kw: filter_rows(self.df, **kw),
            "group_and_aggregate": lambda **kw: group_and_aggregate(self.df, **kw),
            "top_n": lambda **kw: top_n(self.df, **kw),
            "compare_periods": lambda **kw: compare_periods(self.df, **kw),
            "make_chart": lambda **kw: make_chart(self.df, **kw)
        }

    def run(self, user_question: str) -> str:
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful data analyst. Use the provided tools to inspect data and answer questions accurately. Only invoke tools using the structured function call format."
            },
            {"role": "user", "content": user_question}
        ]
        
        trace = []
        
        for step in range(1, self.max_steps + 1):
            print(f"\n[Step {step}] Executing step...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            
            msg = response.choices[0].message
            assistant_msg = {
                "role": "assistant",
                "content": msg.content or ""
            }
            
            if msg.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in msg.tool_calls
                ]
            
            messages.append(assistant_msg)
            
            if not msg.tool_calls:
                print(f"[Step {step}] Final answer received.")
                trace.append({"step": step, "type": "final_answer", "content": msg.content})
                self._save_trace(trace)
                return msg.content

            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except Exception as e:
                    arguments = {}

                print(f"[Step {step}] Tool Call: {func_name}({arguments})")
                
                try:
                    if func_name in self.tools_map:
                        res = self.tools_map[func_name](**arguments)
                    else:
                        res = {"error": f"Tool '{func_name}' does not exist"}
                except Exception as e:
                    res = {"error": str(e)}

                trace.append({
                    "step": step,
                    "type": "tool_call",
                    "tool": func_name,
                    "args": arguments,
                    "result": res
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(res)
                })

        self._save_trace(trace)
        return "Max step iteration cap reached without final answer."

    def _save_trace(self, trace: list):
        with open("agent_trace.json", "w") as f:
            json.dump(trace, f, indent=2)

if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-01", "2024-02-01", "2024-02-01"],
        "product": ["A", "B", "A", "B"],
        "revenue": [100, 200, 150, 400]
    })
    
    agent = DataAnalystAgent(sample_data)
    answer = agent.run("Which product generated highest total revenue, and can you plot a bar chart for total revenue per product?")
    print("\n--- Answer ---")
    print(answer)
