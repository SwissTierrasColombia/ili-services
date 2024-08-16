FROM ubuntu:22.04

# Update repository OS
RUN apt-get upgrade
RUN apt-get update -y

# SO deps
RUN apt-get install -y curl \
                       vim;

# Install OpenJDK-8
RUN apt-get install -y openjdk-8-jdk && \
    apt-get clean;

# Fix certificate issues
RUN apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# Python and python deps
RUN apt-get -y install \
    python3 \
    python3-pip \
    python3-pyodbc;

# Python pip installs
RUN pip3 install --upgrade pip
#RUN apt-get install -y xvfb

# Install requirements
#RUN pip3 install --no-cache-dir -r /app/requirements.txt

RUN pip3 install PyQt5 \
                 requests \
                 psycopg2-binary \
                 nose2

# Copy project data
WORKDIR /app
COPY ../. /app

RUN chmod +x /app/scripts/run-docker-tests.sh

ENV LANG=C.UTF-8