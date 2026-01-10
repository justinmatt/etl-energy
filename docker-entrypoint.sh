#!/usr/bin/env bash
set -e

# Detect correct JAVA_HOME for amd64 or arm64
if [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
elif [ -d "/usr/lib/jvm/java-17-openjdk-arm64" ]; then
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"
else
    echo "Java 17 not found" >&2
    exit 1
fi

export PATH="$JAVA_HOME/bin:$PATH"

echo "Using JAVA_HOME=$JAVA_HOME"

exec "$@"
