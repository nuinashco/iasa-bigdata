FROM apache/spark:4.0.4-scala2.13-java21-ubuntu

USER root
# Executors must run the same Python minor version as the driver (the notebook kernel, 3.13);
# the official python3 image ships Ubuntu's 3.10, which PySpark rejects for UDFs and RDD code.
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv
RUN UV_PYTHON_INSTALL_DIR=/opt/python uv python install 3.13 \
    && ln -s "$(UV_PYTHON_INSTALL_DIR=/opt/python uv python find 3.13)" /usr/local/bin/python3.13 \
    && python3.13 --version

USER spark
