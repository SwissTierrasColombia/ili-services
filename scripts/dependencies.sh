#!/bin/bash

# Define the repository URL and the destination directory
REPO_URL="https://github.com/opengisch/QgisModelBakerLibrary"
DESTINATION_DIR="app/libs"
CLONE_DIR="QgisModelBakerLibrary" # Temporary name for the cloned directory
RELEASE_TAG="v1.7.0" # The release tag to checkout

# Check if Git is installed using `which` instead of `command -v`
if ! which git > /dev/null; then
    echo "Git is not installed or not in your PATH. Please install it to continue."
    exit 1
fi

# Clone the repository
echo "Cloning the repository from $REPO_URL..."
git clone $REPO_URL

# Check if the clone directory exists
if [ ! -d "$CLONE_DIR" ]; then
    echo "Failed to clone the repository. Please check the repository URL and your internet connection."
    exit 1
fi

# Change directory to the cloned repository
cd $CLONE_DIR

# Checkout the specified release tag
echo "Checking out release $RELEASE_TAG..."
git checkout tags/$RELEASE_TAG

# Verify checkout was successful
if [ "$?" -ne 0 ]; then
    echo "Failed to checkout release $RELEASE_TAG. Please check the release tag and try again."
    exit 1
fi

# Change back to the original directory
cd ..

# Create the destination directory if it doesn't exist
if [ ! -d "$DESTINATION_DIR" ]; then
    mkdir -p $DESTINATION_DIR
fi

# Copy the modelbaker folder to the desired path
echo "Copying the modelbaker folder to $DESTINATION_DIR..."
cp -r $CLONE_DIR/modelbaker "$DESTINATION_DIR/"

# Check if the copy was successful
if [ "$?" -eq 0 ]; then
    echo "The modelbaker folder has been successfully copied to $DESTINATION_DIR."
else
    echo "There was an error copying the modelbaker folder. Please check permissions and the destination path."
    exit 1
fi

# Remove cloned directory if no longer needed
rm -rf $CLONE_DIR

echo "Process completed."
