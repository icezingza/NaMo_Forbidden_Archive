# --- Builder Stage ---
# This stage installs dependencies and builds wheels.
FROM python:3.12-slim-bookworm as builder

# Set environment variables for a clean build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
# This stage copies the built dependencies and application code.
FROM python:3.12-slim-bookworm as final

# Set the working directory in the container
WORKDIR /app

# Create a non-root user to run the application
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the rest of the application's code
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

# Set the path to include the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Command to run the application (Cloud Run sets the PORT env var)
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]