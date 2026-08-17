# LeftyDevKit 3D + Corruption Ledger — single self-contained container.
# Serves the particle landing site, the live corruption ledger API, and the
# ledger explorer on ONE port (8000). Deployable as-is (Coolify/Docker etc.).
FROM python:3.11-slim

WORKDIR /app

# Combined server (site + /api/* + /tool) and the vendored ledger tracker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/app.py .
COPY server/tracker ./tracker
COPY server/web ./web
COPY server/data ./data

# The 3D site (index.html + assets) lives at the repo root.
COPY index.html .
COPY assets ./assets

# Rebuild the ledger export inside the image (uses the shipped DB snapshot).
RUN cd /app && python -c "import tracker.export as e; e.run()" || true

EXPOSE 3000
CMD ["python", "app.py"]