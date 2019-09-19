# ====================================================================== #
# Android SDK Docker Image
# ====================================================================== #

# Base image
# ---------------------------------------------------------------------- #
FROM alpine:3.8

# Author
# ---------------------------------------------------------------------- #
LABEL maintainer "contact@giorgiopiatti.ch"

RUN apk update
RUN apk add --no-cache python3
RUN pip3 install PyPDF2

RUN apk add --no-cache imagemagick
RUN apk add --no-cache pdftk

RUN apk add --no-cache openssh
RUN apk add --no-cache bash

ENV RCLONE_VERSION=current
ENV ARCH=amd64

RUN apk --no-cache add ca-certificates fuse wget \
    && cd /tmp \
    && wget -q http://downloads.rclone.org/rclone-${RCLONE_VERSION}-linux-${ARCH}.zip \
    && unzip /tmp/rclone-${RCLONE_VERSION}-linux-${ARCH}.zip \
    && mv /tmp/rclone-*-linux-${ARCH}/rclone /usr/bin \
    && rm -r /tmp/rclone* 

#RUN addgroup alpha \
#   && adduser -h /home/alpha -s /bin/ash -G alpha -D alpha

#USER alpha

COPY script /root/script

ENTRYPOINT [ "python3", "/root/script/sync.py" ]

VOLUME ["/root/.config/rclone/"]
