# Python base image
FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory in the new user's home
WORKDIR /home/appuser/talia_bot

# Copy and install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the package contents and change ownership
COPY --chown=appuser:appuser bot bot

# Switch to the non-root user
USER appuser

# Add a basic health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python3 -c "import os; exit(0) if os.path.exists('bot/main.py') else exit(1)"

# Run the bot via the package entrypoint
CMD ["python", "-m", "bot.main"]
