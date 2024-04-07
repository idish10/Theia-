FROM python:latest

RUN apt-get update
RUN apt install -y make automake gcc g++ subversion python3-dev openssh-client
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN pip3 install numpy
RUN pip3 install websockets
RUN pip3 install web3
RUN pip3 install pymongo
RUN pip3 install pycoingecko
RUN pip3 install etherscan-python
RUN pip3 install py-etherscan-api



# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements

COPY . /app
WORKDIR /app/
RUN  python setup.py install
RUN pip3 install pymongo[srv]

CMD ["python3", "pattrn_robust_tracking/utils/Web3_Transaction_Code.py"]
