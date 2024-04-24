FROM node:18-alpine AS frontend-builder

# For the user setup script
RUN apk update && apk add python3 && rm -rf /var/cache/apk/*

# Use yarn v2+, not default yarn v1
RUN yarn global add @yarnpkg/cli-dist
ENV PATH=/build/.yarn/bin:${PATH}

## This block has to be copied into every FROM section but you can override
## all instances at once using args in docker-compose.yml
#
# Use different users for building app as non-root vs running application
ARG BUILD_USER=website-build
ARG BUILD_UID=65940
# Shared group
ARG RUN_USER=website-run
ARG RUN_UID=65941
# Group for data files
ARG DATA_GROUP=website-data
ARG DATA_GID=65942
COPY docker/user_setup.py /tmp
RUN python3 /tmp/user_setup.py \
    --build-user=${BUILD_USER} --build-uid=${BUILD_UID} \
    --run-user=${RUN_USER} --run-uid=${RUN_UID} \
    --data-group=${DATA_GROUP} --data-gid=${DATA_GID} \
    && rm /tmp/user_setup.py

RUN mkdir /build && chown ${BUILD_USER}:${BUILD_USER} /build
WORKDIR /build
USER ${BUILD_USER}

COPY frontend/package.json frontend/yarn.lock ./

ENV PATH=/build/.yarn/bin:${PATH}
ENV YARN_NODE_LINKER=node-modules
RUN yarn install --frozen-lockfile

COPY --chown=${BUILD_USER} frontend .
RUN node_modules/.bin/vite build


FROM python:3.10-slim AS python-builder

# build-essential is needed for uwsgi
RUN apt update && apt install -y build-essential && rm -rf /var/lib/apt/lists

## This block has to be copied into every FROM section but you can override
## all instances at once using args in docker-compose.yml
#
# Use different users for building app as non-root vs running application
ARG BUILD_USER=website-build
ARG BUILD_UID=65940
# Shared group
ARG RUN_USER=website-run
ARG RUN_UID=65941
# Group for data files
ARG DATA_GROUP=website-data
ARG DATA_GID=65942
COPY docker/user_setup.py /tmp
RUN python3 /tmp/user_setup.py \
    --build-user=${BUILD_USER} --build-uid=${BUILD_UID} \
    --run-user=${RUN_USER} --run-uid=${RUN_UID} \
    --data-group=${DATA_GROUP} --data-gid=${DATA_GID} \
    && rm /tmp/user_setup.py

RUN mkdir /app && chown ${BUILD_USER}:${BUILD_USER} /app
WORKDIR /app
USER ${BUILD_USER}

RUN pip install pipenv

ENV PATH=/home/${BUILD_USER}/.local/bin:${PATH}

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN PIPENV_VENV_IN_PROJECT=1 pipenv sync



FROM python:3.10-slim AS python-run

RUN apt update && apt install -y \
    tini \
    media-types `# for uwsgi static serving` \
    sqlite3 `# for maintenance, init` \
    && rm -rf /var/lib/apt/lists


## This block has to be copied into every FROM section but you can override
## all instances at once using args in docker-compose.yml
#
# Use different users for building app as non-root vs running application
ARG BUILD_USER=website-build
ARG BUILD_UID=65940
# Shared group
ARG RUN_USER=website-run
ARG RUN_UID=65941
# Group for data files
ARG DATA_GROUP=website-data
ARG DATA_GID=65942
COPY docker/user_setup.py /tmp
RUN python3 /tmp/user_setup.py \
    --build-user=${BUILD_USER} --build-uid=${BUILD_UID} \
    --run-user=${RUN_USER} --run-uid=${RUN_UID} \
    --data-group=${DATA_GROUP} --data-gid=${DATA_GID} \
    && rm /tmp/user_setup.py

RUN mkdir /app && chown ${BUILD_USER}:${BUILD_USER} /app
WORKDIR /app
USER ${BUILD_USER}

COPY --from=python-builder /app /app
ENV PATH=/app/.venv/bin:${PATH}

COPY --chown=${BUILD_USER} . .

RUN mkdir frontend/static && mkdir frontend/static/dist
COPY --from=frontend-builder /build/static/dist frontend/static/dist

ENV DJANGO_SETTINGS_MODULE=website.prod_settings

RUN ./manage.py collectstatic

USER ${RUN_USER}

# umask 0002 so that most files + folders get group permissions for access
# by DATA_GROUP
ENTRYPOINT ["sh", "-c", "umask 0002 && exec tini -- \"${@}\"", ""]

CMD uwsgi --uwsgi-socket=0.0.0.0:8001 \
    --strict --enable-threads --need-app \
    --wsgi-file=website/wsgi.py \
    --check-static public --static-map=/media=media
