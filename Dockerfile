# ====================================================================== #
# Android SDK Docker Image
# ====================================================================== #

# Base image
# ---------------------------------------------------------------------- #
FROM rclone/rclone:latest

# Author
# ---------------------------------------------------------------------- #
LABEL maintainer "contact@giorgiopiatti.ch"

RUN apk --update add python3
RUN pip3 install PyPDF2

RUN apk --update add imagemagick

COPY script /script


RUN apk add --no-cache bash
ENTRYPOINT [ "bash" ]

VOLUME /root/.config/rclone/
