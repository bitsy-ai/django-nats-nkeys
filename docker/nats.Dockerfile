from nats:2.8-alpine

COPY nats-entrypoint.sh /usr/local/bin
ENTRYPOINT ["/usr/local/bin/nats-entrypoint.sh"]
CMD ["nats-server", "--config", "/etc/nats/nats-server.conf"]