FROM ubuntu:18.04

WORKDIR /app

ADD bin/refdiff_lib/ /app/bin/refdiff_lib/
ADD bin/refdiff.jar /app/bin/refdiff.jar
ADD scripts/ /app/scripts
ADD main.py /app/main.py
ADD requirements.txt /app/requirements.txt

#Python 3
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install pip
RUN apt-get update && apt-get install -y python3-distutils python3-setuptools
RUN python3.7 -m pip install pip --upgrade pip

# Libraries
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Git 
RUN apt-get -y install git

# Graphviz
RUN apt-get -y install graphviz

# JDK8
RUN apt-get update && \
	apt-get install -y openjdk-8-jdk && \
	apt-get install -y ant && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* && \
	rm -rf /var/cache/oracle-jdk8-installer;
	
RUN apt-get update && \
	apt-get install -y ca-certificates-java && \
	apt-get clean && \
	update-ca-certificates -f && \
	rm -rf /var/lib/apt/lists/* && \
	rm -rf /var/cache/oracle-jdk8-installer;

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

RUN export JAVA_HOME

# RUN python3.7 /app/main.py alinebrito/refactoring-graph-fowler java

CMD sleep 99999999999