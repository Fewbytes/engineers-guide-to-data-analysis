# Metric gen

This is a pseudo web service for training purposes. It creates HTTP requests which are fed directly to FastAPI ASGI app, without a socket based webserver. Everything (client and server) is running within a single process.