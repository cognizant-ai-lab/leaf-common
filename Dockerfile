# AUTHOR: Darren Sargent
# DESCRIPTION: Docker file for leaf-common.

FROM python:3.6-stretch

ENV APP_HOME /usr/local/cognizant
ARG MY_GITHUB_PW

USER root

# Copy requirements file only. That way, we don't have to rebuild the requirements layer, which takes a long time,
# each time the source changes.
COPY ./requirements.txt ${APP_HOME}/leaf-common/requirements.txt
RUN pip3 install -r ${APP_HOME}/leaf-common/requirements.txt

# Copy rest of source dir
COPY ./ ${APP_HOME}/leaf-common/

USER root
WORKDIR ${APP_HOME}

