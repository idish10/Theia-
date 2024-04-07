FROM python:3.8-slim

RUN apt-get update
RUN apt install -y make automake gcc g++ subversion python3-dev openssh-client
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip3 install coralogix
RUN pip3 install coralogix-logger
RUN pip3 install pymongo

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app
WORKDIR /app/
RUN  python setup.py install
RUN pip3 install pymongo[srv]

RUN chmod +x ./osmosisd-6.4.0-linux-amd64

CMD ["python", "pattrn_robust_tracking/loggers/osmo/log.py"]
# CMD ["ls", "-l"]
