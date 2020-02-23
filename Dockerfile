# ====================================================================== #
# Remarkable sync container image
# ====================================================================== #

# Builder image
# ---------------------------------------------------------------------- #
FROM golang:1.13.8-alpine as builder
RUN mkdir /build
RUN apk update
RUN apk add --no-cache git
RUN git clone https://github.com/giorgiopiatti/rm2pdf /build/
WORKDIR /build
RUN go mod download
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-extldflags "-static"' -o rm2pdf ./

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

ARG RCLONE_VERSION=current
ARG ARCH=amd64

RUN apk --no-cache add ca-certificates fuse wget \
    && cd /tmp \
    && wget -q http://downloads.rclone.org/rclone-${RCLONE_VERSION}-linux-${ARCH}.zip \
    && unzip /tmp/rclone-${RCLONE_VERSION}-linux-${ARCH}.zip \
    && mv /tmp/rclone-*-linux-${ARCH}/rclone /usr/bin \
    && rm -r /tmp/rclone* 

COPY script /root/script
COPY --from=builder /build/rm2pdf /root/script/

WORKDIR /root/script
ENTRYPOINT [ "python3", "/root/script/sync.py" ]

VOLUME ["/root/.config/rclone/"]
