# Use Ubuntu as the base image
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y iputils-ping \
                       nano \
                       coreutils \
                       openssh-client \
                       sudo \
                       wget \
                       apache2 \
                       python3 \
                       python3-venv \
                       python3-pip \
                       ca-certificates \
                       curl \
                       gnupg \
                       lsb-release \
                       qemu-system \
                       binfmt-support \
                       qemu-user-static

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages in the virtual environment
RUN pip install redis

# Expose the Apache server port
EXPOSE 80

# Create a directory for volume data
RUN mkdir -p /VolumeData

# Copy the startup script into the container
COPY ApacheStart.sh /usr/bin/ApacheStart
RUN chmod +x /usr/bin/ApacheStart

# Define the command to run ApacheStart script
CMD ["/usr/bin/ApacheStart"]
