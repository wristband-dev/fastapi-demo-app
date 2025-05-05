FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . /app/

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0
ENV ENV=staging

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run.py"] 