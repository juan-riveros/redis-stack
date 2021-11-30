FROM python:3-slim

ARG OUTPUT_FILENAME
ARG DIST_DIR
ENV APP_DIR /app
ENV XDG_CONFIG_HOME /app/.config

ENV PATH="$APP_DIR:$PATH"
ENV UID=1000
ENV GID=1000

RUN groupadd --gid $GID --system appgroup && useradd --system --create-home --home-dir $APP_DIR --gid $GID --uid $UID appuser
USER appuser
WORKDIR $APP_DIR
COPY $DIST_DIR/$OUTPUT_FILENAME $APP_DIR/cmd
CMD ["sh", "-c", "cmd"]
