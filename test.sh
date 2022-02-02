#!/usr/bin/env bash

poetry run coverage \
              run --omit="/home/circleci/.cache/pypoetry/virtualenvs" \
              --branch \
              -m pytest \
              --junit-xml=.junit.xml