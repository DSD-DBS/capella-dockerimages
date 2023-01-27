#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -ex

export CAPELLA_VERSION=${CAPELLA_VERSION:-6.0.0} # Only 6.0.0 supported for now


echo "Build for Capella version $CAPELLA_VERSION"

# Clean tmp directory
mkdir -p /tmp/capella
cd /tmp/capella

# Print maven version
mvn --version

# Clone Capella Github repository
git clone https://github.com/eclipse/capella
cd capella
git checkout v$CAPELLA_VERSION
cd ..

# Install JDK 11
curl -L -o jdk11-linux.tar.gz https://api.adoptium.net/v3/binary/latest/11/ga/linux/aarch64/jdk/hotspot/normal/eclipse?project=jdk
tar xf jdk11-linux.tar.gz
export PATH=$(find /tmp/capella -depth 2 -name "bin"):${PATH}

# Print java version
java -version

cd capella

# Modify pom.xml and inject architecture
python /opt/inject_architecture_into_pom.py

# Build Capella
mvn clean verify -f releng/plugins/org.polarsys.capella.targets/pom.xml

# Inject JRE 17 (Linux)
curl -L -o linuxJRE.tar.gz https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jre/hotspot/normal/eclipse?project=jdk
mkdir -p linuxJRE/jre
tar -xf linuxJRE.tar.gz --strip-components 1 -C linuxJRE/jre

# Inject JRE 17 (Linux)
curl -L -o linuxJRE-aarch64.tar.gz https://api.adoptium.net/v3/binary/latest/17/ga/linux/aarch64/jre/hotspot/normal/eclipse?project=jdk
mkdir -p linuxJRE-aarch64/jre
tar -xf linuxJRE-aarch64.tar.gz --strip-components 1 -C linuxJRE-aarch64/jre

# Inject JRE 17 (macOS)
curl -L -o macJRE.tar.gz https://api.adoptium.net/v3/binary/latest/17/ga/mac/x64/jre/hotspot/normal/eclipse?project=jdk
mkdir -p macJRE/jre
tar -xf macJRE.tar.gz --strip-components 1 -C macJRE/jre

# Inject JRE 17 (macOS)
curl -L -o macJRE-aarch64.tar.gz https://api.adoptium.net/v3/binary/latest/17/ga/mac/aarch64/jre/hotspot/normal/eclipse?project=jdk
mkdir -p macJRE-aarch64/jre
tar -xf macJRE-aarch64.tar.gz --strip-components 1 -C macJRE-aarch64/jre

# Inject JRE 17 (Windows)
curl -L -o winJRE.zip https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk
mkdir -p winJRE
unzip winJRE.zip -d winJRE/jre
mv winJRE/jre/*/* winJRE/jre

mvn clean verify -f pom.xml -DjavaDocPhase=none -Pfull

mv /tmp/capella/capella/releng/plugins/org.polarsys.capella.rcp.product/target/products /output
