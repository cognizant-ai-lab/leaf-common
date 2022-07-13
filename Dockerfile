# AUTHOR: Darren Sargent
# DESCRIPTION: Docker file for leaf-common.

FROM python:3.8-slim

ENV APP_HOME /usr/local/cognizant

USER root

# Wheel is already installed in the FROM image
RUN pip3 install pip==22.1.2

# Copy requirements file only. That way, we don't have to rebuild the requirements layer, which takes a long time,
# each time the source changes.
COPY ./requirements.txt ${APP_HOME}/leaf-common/requirements.txt
RUN pip3 install -r ${APP_HOME}/leaf-common/requirements.txt

# Copy rest of source dir
COPY ./ ${APP_HOME}/leaf-common/

USER root
WORKDIR ${APP_HOME}

