from pydantic import BaseModel, Field
import sys

sys.path.append("/Users/akhileshjain/Documents/FuturePath/incident_agent")
from runbook_agent.llms.open_ai import chat_completion_request_instructor
from typing import List
import requests
import time


class IssueResponse(BaseModel):
    potential_issue: str = Field(
        ..., description="The potential issue that we identified"
    )
    log_items: str = Field(
        ..., description="Select the log lines that coudl explain the potential issue"
    )
    insights: str = Field(
        ...,
        description="Provide a summary of the logs that we identified to explain the potential issue",
    )


class LogAnalysisResponse(BaseModel):
    issues: List[IssueResponse] | None = Field(
        None, description="List of potential issues that we identified"
    )


class LogAnalysisAgent:
    def preprocess_logs(self, logs: str, chunk_size: int) -> List[str]:
        log_lines = logs.split("\n")
        log_chunks = [
            log_lines[i : i + chunk_size] for i in range(0, len(log_lines), chunk_size)
        ]
        return log_chunks

    def load_log_weblink(self, log_file_path: str) -> str:
        response = requests.get(log_file_path)
        return response.text

    def print_issues(self, issues: List[IssueResponse]):
        for issue in issues:
            print("-" * 100)
            print("Potential Issue: ", issue.potential_issue)
            print("Log Items: ", issue.log_items)
            print("Insights: ", issue.insights)

    def analyse_logs(
        self, log_file_path: str, chunk_size: int = 1000
    ) -> LogAnalysisResponse:
        start_time = time.time()
        logs_content = self.load_log_weblink(log_file_path)
        end_time = time.time()
        print(f"Time taken to load log weblink: {end_time - start_time} seconds")
        start_time = time.time()
        numbered_logs = self.preprocess_logs(logs_content, chunk_size)
        end_time = time.time()
        print(f"Time taken to preprocess logs: {end_time - start_time} seconds")
        for idx, each_log in enumerate(numbered_logs):
            print(f"processing {idx} of {len(numbered_logs)}")
            prompt = f"""
            You are a log analysis expert. You are given a list of machine logs. Your goal is to identify log lines that could potentially explain the following issues:
            1. The machine is experiencing high CPU usage.
            2. The machine is running low on disk space.

            if an issue is not found, ignore it from mentioning in the response.

            Your steps should be:
            - Skim through each provided log line.
            - Identify any log entries that indicate or suggest high CPU usage (e.g., warnings or errors mentioning CPU load, processes using excessive CPU time, CPU temperature warnings).
            - Identify any log entries that indicate or suggest low disk space (e.g., disk usage threshold exceeded, out-of-space errors, failed writes due to insufficient storage).
            - From the logs you identify, extract and return the lines that would help analyze the cause of these issues.
            - Provide a summarized explanation of why these logs might explain the potential issue.
            - If no relevant logs (i.e., no errors or warnings related to CPU or disk issues) are found, return None.

            Here are the logs:
            {each_log}
            """
            response = chat_completion_request_instructor(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt.format(logs=each_log)}],
                response_model=LogAnalysisResponse,
            )
            if response.issues:
                return response
        return None
