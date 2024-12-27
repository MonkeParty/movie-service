# Use Alpine-based Python image
FROM python:3.12-slim

WORKDIR /app

# Copy the source code into the container.
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app

RUN chmod +x /app/docker/launch.sh

ENV PYTHONPATH="/app"

# Command to run the application with automatic reload
CMD ["/app/docker/launch.sh"] 