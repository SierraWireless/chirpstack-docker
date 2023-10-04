# AirVantage Middleware

This folder contains a Dockerfile which starts a HTTP server waiting for requests on port 8100.
When requests are received, only "up" [Events](https://www.chirpstack.io/docs/chirpstack/integrations/events.html) with FPort 31 are handled.
The expected payload is 8-byte long with Latitude, Longitude and Altitude encoded as described [here](https://github.com/Lora-net/LoRaMac-node/blob/2bf36bde72f68257eb96b5c00900619546bedca8/src/system/gps.c#L113).

Once decoded the Location data is encoded in JSON and pushed to the related AirVantage system with REST API. The AirVantage system S/N must be set to the LoRa Device EUI.

## Chirpstack Configuration

An [HTTP integration](https://www.chirpstack.io/docs/chirpstack/integrations/http.html) must be set up in Chirpstack Application Server to forward the LoRa events to the Airvantage Middleware. The settings to be used are the following:
* Payload encoding: JSON
* Event endpoint URL: http://\<Chirpstack IP address\>:8100
