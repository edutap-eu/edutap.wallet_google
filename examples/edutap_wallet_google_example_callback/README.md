# Example callback service for Google

This service logs received data to a file and to stdout.

It logs space separated:
- `class_id`
- `object_id`
- `event_type`
- `exp_time_millis`
- `count`
- `nonce`

# Configuration environment

Environment variables are used for configuration.

- `EDUTAP_WALLET_GOOGLE_EXAMPLE_CALLBACK_LOG_FILE`

   The name and location of the log file.
   Default is relative to current working directory: `./callback_log.txt`.

From `edutap.wallet_google`:

- `EDUTAP_WALLET_GOOGLE_HANDLER_PREFIX_CALLBACK`

   The path prefix of the callback in the browser.
   Default: Empty string (no prefix)

- `EDUTAP_WALLET_GOOGLE_HANDLER_CALLBACK_VERIFY_SIGNATURE`

  Whether to verify the signature (`1`) in the callback or not (`0`).
  Default: `1`


## Local usage (dev)

Installation (execute in this folder)

```shell
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate
```

Run with
```shell
fastapi dev edutap_wallet_google_example_callback.py
```

## As Docker container

### Build image and check container

In the root of the repository (in `../..` relative to the location of this `README.md`), run:

```shell
docker buildx build --progress=plain --no-cache -f examples/edutap_wallet_google_example_callback/Dockerfile -t edutap_wallet_google_example_callback .
```

Then run the container interactive to verify its working:
```shell
docker run -it edutap_wallet_google_example_callback
```
Watch out for errors. Stop with Ctrl-c.


### Run on a server

To get actual callbacks from Google the application has to be accessible from the internet and it need to serve on `https` with a valid TLS certificate.
No self-signed certificates are allowed!

A kind of simple way to get an environment up and running is with Docker Swarm, Traefik Web-Proxy with Lets-Encrypt and our container running in there.
Since this is out of scope of this README we point the dear reader to the tutorial website [Docker Swarm Rocks](https://dockerswarm.rocks/traefik/).
The following examples are meant to run in such a cluster, or to be adapted to different environment.
We hope you get the idea.

There is an example swarm deployment in here in `swarm.yml`.
It can be deployed on the cluster.
The public domain must be configured using the environment variable `EDUTAP_WALLET_GOOGLE_EXAMPLE_DOMAIN`.
A TLS certificate will be issued automatically using Lets Encrypt.

Example: `export EDUTAP_WALLET_GOOGLE_EXAMPLE_DOMAIN=edutap-wallet-google-callback.example.com`

```shell
docker stack deploy swarm.yml -c swarm.yml edutap_wallet_google_example_callback
```
