#!/bin/bash
echo "🚀 Starting OmniCoreAgent Documentation Deployment..."
if ! command -v mintlify &> /dev/null; then
    npm install -g mintlify
fi
mintlify broken-links
echo "✅ Documentation links validated."
echo "ℹ️  To deploy, push your changes to the configured branch in your Git repository."
