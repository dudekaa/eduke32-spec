#!/bin/bash
#

set -ue

FILENAME="eduke32.spec"

rpmdev-bumpspec -r "$FILENAME"
