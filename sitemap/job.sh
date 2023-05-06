#!/bin/bash

/usr/local/bin/docker-compose -f docker-compose-prod.yml run --rm -T --name `uuidgen` batch-sitemap
