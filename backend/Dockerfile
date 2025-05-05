FROM python:3.11-slim

WORKDIR /app

# Copy requirements and application code
COPY pyproject.toml run.py /app/
COPY src/ /app/src/
COPY wristband/ /app/wristband/

# Install pip and dependencies
RUN pip install .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run.py"] 