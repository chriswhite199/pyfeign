#!/usr/bin/env bash

poetry run mypy --junit-xml .mypy.xml --html-report mypyhtml pyfeign