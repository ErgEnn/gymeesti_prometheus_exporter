# gymeesti_prometheus_exporter
Python proxy server to make [Gym Eesti OÜ](https://www.gymeesti.ee/) gyms people count metrics available for [Prometheus](https://prometheus.io/)

## Usage
Update `docker-compose.yml` with your Gym Eesti email and password and run
`docker-compose up`

This runs server on port `5000`. Be sure to forward the port if you are running prometheus externally. Or if prometheus is also running in docker container use external network configuration to link those containers.

## Note
Default scraping time of 1 minute is too often! Change it to something like 15m. We don't want to DDOS the service and get blocked out.