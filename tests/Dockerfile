FROM python:3.11-slim

WORKDIR /app

COPY auth_service/requirements.txt ./auth_requirements.txt
RUN pip install --no-cache-dir -r auth_requirements.txt

COPY tests/requirements.txt ./tests_requirements.txt
RUN pip install --no-cache-dir -r tests_requirements.txt

COPY auth_service ./auth_service
COPY tests ./tests

ENTRYPOINT [ "bash", "-lc", "\
    cd auth_service && alembic upgrade head && \
    cd /app && pytest --disable-warnings -s \
" ]
