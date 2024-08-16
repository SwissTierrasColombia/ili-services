#!/bin/bash

# Note: the version of ili2db and ilivalidator must be the same as the one used in the source code
# iliservices/modelbaker/iliwrapper/ili2dbtools.py
# iliservices/modelbaker/iliwrapper/ilivalidator/ilivalidatortools.py

ILI2DB_VERSION="5.1.0"
ILIVALIDATOR_VERSION="1.14.1"

# Target directory
ILI2DB_DEST_DIR="iliservices/modelbaker/iliwrapper/bin"
ILIVALIDATOR_DEST_DIR="iliservices/modelbaker/iliwrapper/ilivalidator/bin"

# Create the target directory if it doesn't exist
mkdir -p "$ILI2DB_DEST_DIR"
mkdir -p "$ILIVALIDATOR_DEST_DIR"

# Elimina las librerías existentes para hacer una descarga limpia
# rm -rf "$ILI2DB_DEST_DIR/*"
# rm -rf "$ILIVALIDATOR_DEST_DIR/*"

# Download ili2pg
echo "Downloading ili2pg..."
wget https://downloads.interlis.ch/ili2pg/ili2pg-${ILI2DB_VERSION}.zip -P "$ILI2DB_DEST_DIR"

# Download ili2gpkg
echo "Downloading ili2gpkg..."
wget https://downloads.interlis.ch/ili2gpkg/ili2gpkg-${ILI2DB_VERSION}.zip -P "$ILI2DB_DEST_DIR"

# Download ilivalidator
echo "Downloading ilivalidator..."
wget https://downloads.interlis.ch/ilivalidator/ilivalidator-${ILIVALIDATOR_VERSION}.zip -P "$ILIVALIDATOR_DEST_DIR"

# Unzip files into the target directory
echo "Unzipping files..."
unzip -o "$ILI2DB_DEST_DIR/ili2pg-${ILI2DB_VERSION}.zip" -d "$ILI2DB_DEST_DIR/ili2pg-${ILI2DB_VERSION}"
unzip -o "$ILI2DB_DEST_DIR/ili2gpkg-${ILI2DB_VERSION}.zip" -d "$ILI2DB_DEST_DIR/ili2gpkg-${ILI2DB_VERSION}"
unzip -o "$ILIVALIDATOR_DEST_DIR/ilivalidator-${ILIVALIDATOR_VERSION}.zip" -d "$ILIVALIDATOR_DEST_DIR/ilivalidator-${ILIVALIDATOR_VERSION}"

# Clean up downloaded ZIP files
echo "Cleaning up downloaded files..."
rm "$ILI2DB_DEST_DIR/ili2pg-${ILI2DB_VERSION}.zip"
rm "$ILI2DB_DEST_DIR/ili2gpkg-${ILI2DB_VERSION}.zip"
rm "$ILIVALIDATOR_DEST_DIR/ilivalidator-${ILIVALIDATOR_VERSION}.zip"

echo "Process completed."
