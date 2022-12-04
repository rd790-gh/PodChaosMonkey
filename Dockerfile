FROM ubuntu:22.04

# Install python and pip
RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3.8 python3-pip


# Install requirements.txt 
COPY requirements.txt ./
RUN pip install -r requirements.txt


WORKDIR /usr/src/app
COPY pod_chaos_monkey.py ./
CMD ["python3", "/usr/src/app/pod_chaos_monkey.py"]