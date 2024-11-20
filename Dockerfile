# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /mysite

# Copy the requirements file and install dependencies
COPY requirements.txt /mysite//
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /mysite


# Copy the entry point script
COPY entrypoint.sh /mysite/entrypoint.sh
RUN chmod +x /mysite/entrypoint.sh

# Expose ports for Django
EXPOSE 8000

# Run the entrypoint script
CMD ["/mysite/entrypoint.sh"]