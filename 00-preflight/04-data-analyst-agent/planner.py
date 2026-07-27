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

class PlannedAnalystAgent:
    def __init__(self, df: pd.DataFrame, model: str = "llama-3.1-8b-instant"):
        self.df = df
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = model
        self.max_steps = 10
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

    def generate_plan(self, question: str) -> dict:
        prompt = f"""
Given the question: "{question}"
Break it down into a step-by-step checklist.
Return ONLY a valid JSON object matching this structure:
{{
  "goal": "{question}",
  "steps": [
    {{"id": 1, "description": "Inspect schema", "status": "pending"}},
    {{"id": 2, "description": "Aggregate data", "status": "pending"}}
  ]
}}
Do not add markdown backticks outside JSON.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content)
        except Exception:
            return {
                "goal": question,
                "steps": [
                    {"id": 1, "description": "Inspect dataset schema", "status": "pending"},
                    {"id": 2, "description": "Perform necessary aggregation/calculation", "status": "pending"},
                    {"id": 3, "description": "Plot chart if requested and formulate final answer", "status": "pending"}
                ]
            }

    def replan(self, current_plan: dict, surprise_reason: str) -> dict:
        print(f"\n⚡ [RE-PLANNING TRIGGERED] Reason: {surprise_reason}")
        prompt = f"""
Current Plan: {json.dumps(current_plan)}
Surprise/Unexpected Result: {surprise_reason}
Update the pending steps of the plan to adapt to this new discovery.
Return ONLY valid JSON with the same structure.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content)
        except Exception:
            return current_plan

    def display_plan(self, plan: dict):
        print("\n=== AGENT EXECUTION PLAN ===")
        print(f"Goal: {plan.get('goal')}")
        for step in plan.get("steps", []):
            status_icon = "⏳" if step['status'] == "pending" else ("🔄" if step['status'] == "in_progress" else "✅")
            print(f"  [{status_icon}] Step {step['id']}: {step['description']}")
        print("============================\n")

    def run(self, user_question: str) -> str:
        plan = self.generate_plan(user_question)
        self.display_plan(plan)

        messages = [
            {"role": "system", "content": f"You are a structured data analyst. Follow this plan: {json.dumps(plan)}."},
            {"role": "user", "content": user_question}
        ]

        trace = []
        step_idx = 0

        for step_num in range(1, self.max_steps + 1):
            if step_idx < len(plan["steps"]):
                plan["steps"][step_idx]["status"] = "in_progress"
                self.display_plan(plan)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )

            msg = response.choices[0].message
            assistant_msg = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in msg.tool_calls
                ]
            messages.append(assistant_msg)

            if not msg.tool_calls:
                if step_idx < len(plan["steps"]):
                    plan["steps"][step_idx]["status"] = "completed"
                self.display_plan(plan)
                print("Final answer generated.")
                return msg.content

            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except Exception:
                    args = {}

                print(f"[Step {step_num}] Running: {func_name}({args})")
                try:
                    res = self.tools_map.get(func_name, lambda **k: {"error": "Tool missing"})(**args)
                except Exception as e:
                    res = {"error": str(e)}

                # Re-planning Trigger Check (Stretch Goal)
                if isinstance(res, dict) and "error" in res:
                    plan = self.replan(plan, f"Tool {func_name} failed with error: {res['error']}")
                elif isinstance(res, dict) and res.get("row_count", 1) == 0:
                    plan = self.replan(plan, f"Tool {func_name} returned 0 rows. Empty dataset slice!")

                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(res)})
                trace.append({"step": step_num, "tool": func_name, "args": args, "result": res})

            if step_idx < len(plan["steps"]):
                plan["steps"][step_idx]["status"] = "completed"
                step_idx += 1

        return "Max execution cap reached."

if __name__ == "__main__":
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-01", "2024-02-01", "2024-02-01"],
        "product": ["A", "B", "A", "B"],
        "revenue": [100, 200, 150, 400]
    })
    agent = PlannedAnalystAgent(df)
    ans = agent.run("Calculate total revenue per product, check for outliers, and plot a chart.")
    print("\nANSWER:\n", ans)
