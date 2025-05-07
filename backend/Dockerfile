FROM python:3.11-slim

WORKDIR /app

# Copy requirements and application code
COPY backend/pyproject.toml backend/run.py /app/
COPY backend/src/ /app/src/
COPY backend/wristband/ /app/wristband/

# Install pip and dependencies
RUN pip install .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run.py"] 