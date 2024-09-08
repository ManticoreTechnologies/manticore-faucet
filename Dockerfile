# Step 1: Use the official Python image
FROM python:3.9-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy all necessary files into the container
COPY . /app

# Step 4: Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose Flask port
EXPOSE 5000

# Step 6: Command to start Gunicorn with Flask app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout", "120", "startup:app"]
