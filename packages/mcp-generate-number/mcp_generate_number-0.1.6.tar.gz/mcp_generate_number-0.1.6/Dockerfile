FROM python:3.12-slim
WORKDIR /app

# Install dependencies first to leverage Docker caching
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY mcp_generate_number/ ./mcp_generate_number/

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Run the application
CMD ["python", "-m", "mcp_generate_number.server"] 