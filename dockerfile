# ════════════════════════════════════════════════════════════════
# EGX Pro Terminal v35 — Dockerfile
# Streamlit Application Container
#
# Build:   docker build -t egx-pro-terminal .
# Run:     docker run -p 8501:8501 egx-pro-terminal
# Dev:     docker run -p 8501:8501 -v $(pwd):/app egx-pro-terminal
# With AI: docker run -p 8501:8501 -e GEMINI_API_KEY=AIza... egx-pro-terminal
# ════════════════════════════════════════════════════════════════

FROM python:3.11-slim

# ── Metadata ─────────────────────────────────────────────────
LABEL maintainer="EGX Pro Team"
LABEL version="35.0.0"
LABEL description="EGX Pro Terminal — Professional Egyptian Stock Exchange Analysis"

# ── System dependencies ───────────────────────────────────────
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────
WORKDIR /app

# ── Python dependencies (layer cached separately) ────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────
COPY . .

# ── Runtime directories ───────────────────────────────────────
RUN mkdir -p logs data

# ── Streamlit config ──────────────────────────────────────────
# .streamlit/config.toml is already in the repo
# Secrets must be mounted at runtime — never baked into image:
# docker run -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml egx-pro-terminal

# ── Non-root user (security best practice) ───────────────────
RUN addgroup --system egx && adduser --system --ingroup egx egxuser
RUN chown -R egxuser:egx /app
USER egxuser

# ── Expose Streamlit port ─────────────────────────────────────
EXPOSE 8501

# ── Health check ─────────────────────────────────────────────
HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=30s \
    --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ── Entry point ───────────────────────────────────────────────
CMD ["streamlit", "run", "egx_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--browser.gatherUsageStats=false", \
     "--logger.level=warning"]
