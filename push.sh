#!/bin/bash

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key
ssh-add ~/.ssh/id_ed25519

# Git add all
git add .

# Ask for commit message
echo -n "Commit message: "
read msg

# Default message if empty
if [ -z "$msg" ]; then
  msg="Auto commit"
fi

git commit -m "$msg"

# Push to origin main
git push -u origin main
