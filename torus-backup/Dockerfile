FROM alpine:latest
RUN apk add --no-cache bash tar curl
RUN addgroup -S torus && adduser -S torus -G torus
COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh && chown torus:torus /usr/local/bin/backup.sh
WORKDIR /backups
RUN chown -R torus:torus /backups
USER torus
VOLUME /backups
CMD ["/usr/local/bin/backup.sh"]
