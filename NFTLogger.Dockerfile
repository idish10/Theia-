###########################################################################
#
# Pattrn Capital - NFT Logger
#
###########################################################################

# Take the base image with cron installed
FROM ubuntu

# Update package manager
RUN apt-get -y update
RUN apt install -y make automake gcc g++ subversion python3-dev openssh-client
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

# Install program's used packages
RUN pip3 install coralogix
RUN pip3 install coralogix-logger
RUN pip3 install pycoingecko
RUN pip3 install opensea-api
RUN pip3 install pymongo

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Copy project

COPY . /app
WORKDIR /app/

RUN python3 setup.py install
RUN pip3 install pymongo[srv]

CMD ["python3", "-u", "pattrn_robust_tracking/loggers/nft/log.py"]
