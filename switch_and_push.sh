#!/bin/bash
# Script to switch to 'saurabhhhcodes' and push

echo "1. Logging in to GitHub..."
echo "Please follow the prompts to login as 'saurabhhhcodes'"
gh auth login --hostname github.com -p https --web

echo "2. Creating Repository 'saurabhhhcodes/SahayakAI'..."
# Remove old remote if exists
git remote remove origin 2>/dev/null

# Create new repo and push
gh repo create saurabhhhcodes/SahayakAI --public --source=. --remote=origin --push

echo "3. Code Pushed Successfully!"
echo "Now proceed to Render Dashboard to deploy."
