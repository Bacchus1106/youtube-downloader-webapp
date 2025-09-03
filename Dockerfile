# 1. Start with a lean official Python base image.
#    This provides a clean, minimal environment with Python pre-installed.
FROM python:3.11-slim

# 2. Set the working directory inside the container.
#    All subsequent commands will run from this path.
WORKDIR /app

# 3. Install FFmpeg using the system's package manager (apt).
#    - `apt-get update`: Refreshes the list of available packages.
#    - `apt-get install -y ffmpeg`: Installs FFmpeg without asking for confirmation.
#    - `rm -rf /var/lib/apt/lists/*`: Cleans up to keep the final image size smaller.
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file into the container's working directory.
COPY requirements.txt .

# 5. Install the Python dependencies specified in requirements.txt.
#    `--no-cache-dir` disables the pip cache to reduce image size.
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code (app.py, templates/, etc.) into the container.
COPY . .

# 7. Expose the port the app will run on. This makes it available to Render's network.
EXPOSE 5000

# 8. Define the command to run your application using Gunicorn.
#    - `--bind 0.0.0.0:5000`: Binds the server to all network interfaces on the specified port.
#    - `--timeout 300`: Increases the request timeout to 300 seconds (5 minutes) to
#      prevent long video downloads from being prematurely cut off.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]
