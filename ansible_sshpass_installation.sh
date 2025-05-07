#!/bin/bash
echo "Load Test Automation version: 1.4"

# Function to check if a command is installed
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Ansible is installed
if command_exists ansible; then
  echo "Ansible is already installed."
else
  echo "Ansible is not installed. Installing..."
  # Install Ansible with error handling for unmet dependencies
  sudo apt-get update
  sudo apt-get --fix-broken install -y
  sudo apt-get install ansible -y
fi

# Check if sshpass is installed
if command_exists sshpass; then
  echo "sshpass is already installed."
else
  echo "sshpass is not installed. Installing..."
  # Install sshpass with error handling for unmet dependencies
  sudo apt-get update
  sudo apt-get --fix-broken install -y
  sudo apt-get install sshpass -y
fi
