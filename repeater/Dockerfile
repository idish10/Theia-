
###########################################################################
#
# Pattrn Capital - Main Repeater
#
# Usage:
#
#   docker build -t repeater . --build-arg DOCKERHUB_USER=pattrncapital \
#       --build-arg DOCKERHUB_PASSWORD=27wdfwf49eud588dwj \
#       --build-arg REPEAT_MINUTES="*" --build-arg REPEAT_HOURS="*"
#
#   
#
###########################################################################

# Take the base image with cron installed
FROM pattrncapital/ubuntu-cron

# Get user and password arguments for dockerhub
ARG DOCKERHUB_USER
ARG DOCKERHUB_PASSWORD
ARG REPEAT_MINUTES
ARG REPEAT_HOURS

# Update package manager
RUN apt-get -y update

# Install pre-reqs for docker installation
RUN apt-get -y install ca-certificates curl gnupg lsb-release

# Download gpg keys
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg |\
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up docker installation
RUN echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" |\
    tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package manager again
RUN apt-get -y update

# Install docker
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends\
    docker-ce docker-ce-cli containerd.io

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy project
COPY . /

# Set manager for execution
RUN chmod +x /run_manager.sh

# Edit cron file
RUN echo "$REPEAT_MINUTES $REPEAT_HOURS * * * /run_manager.sh >> /tmp/stdout.log 2>> /tmp/stderr.log" >>\
    /var/spool/cron/crontabs/root

ENV DOCKERHUB_USER=$DOCKERHUB_USER
ENV DOCKERHUB_PASSWORD=$DOCKERHUB_PASSWORD
ENV REPEAT_MINUTES=$REPEAT_MINUTES
ENV REPEAT_HOURS=$REPEAT_HOURS

# Run cron and continue forever
ENTRYPOINT cron && docker login -u $DOCKERHUB_USER -p $DOCKERHUB_PASSWORD && tail -f /dev/null
