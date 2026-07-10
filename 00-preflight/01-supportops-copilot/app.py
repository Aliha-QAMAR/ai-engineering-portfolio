"""Streamlit entrypoint that reuses the dashboard UI."""

from dashboard import _is_streamlit_runtime, _run_dashboard


if _is_streamlit_runtime():
	_run_dashboard()
else:
	print("Run this app with: streamlit run app.py")

