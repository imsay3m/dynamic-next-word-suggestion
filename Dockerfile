# --- Base Image ---
FROM python:3.9-slim

# --- Set Working Directory ---
WORKDIR /app

# --- Install Dependencies ---
COPY requirements.txt .

# Install the dependencies. --no-cache-dir reduces the final image size.
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Application Code ---
COPY . .

# --- Expose Port ---
EXPOSE 8000

# --- Run Command ---
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]