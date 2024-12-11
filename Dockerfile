# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN mkdir runbook_agent
ENV PATH="/root/.local/bin:$PATH"
# Set the working directory in the container
WORKDIR /runbook_agent
ENV PYTHONPATH="/runbook_agent:/app/runbook_agent"
COPY /pyproject.toml /runbook_agent
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install 
# Copy the current directory contents into the container
COPY . .
RUN cd event_consumer/core/prisma && prisma generate


# Expose the port FastAPI runs on
EXPOSE 8111

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "runbook_agent.main:app", "--host", "0.0.0.0", "--port", "8111"]