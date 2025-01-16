# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# copy project into container
COPY . /code

# install Python packages
RUN \
    uv venv &&\
    uv pip install --no-cache-dir --upgrade -e /code  &&\
    uv pip install --no-cache-dir --upgrade -e /code/examples/edutap_wallet_google_example_callback

# Place executables in the environment at the front of the path
ENV PATH="/.venv/bin:$PATH"

# Create a directory for logs
RUN mkdir /logs
ENV EDUTAP_WALLET_GOOGLE_EXAMPLE_CALLBACK_LOG_FILE=/logs/callback.log

# set working directory
WORKDIR /code/examples/edutap_wallet_google_example_callback

# run fastapi
CMD ["fastapi", "run", "edutap_wallet_google_example_callback.py", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
