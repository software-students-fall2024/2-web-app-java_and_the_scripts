# Use a slim version of Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the image
WORKDIR /app

# Install dependencies from requirements.txt
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --upgrade pymongo && pip install -r requirements.txt

# Add all files from the current directory to the container
ADD . .

# Expose the port used by the Flask app
EXPOSE 11000

# Ensure FLASK_APP is properly set and Python runs the Flask app
ENV FLASK_APP=app.app:create_app

# Run the Flask app on container start
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=11000"]



