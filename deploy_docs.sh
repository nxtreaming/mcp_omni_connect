#!/bin/bash
echo "🚀 Starting OmniCoreAgent Documentation Deployment..."
npm install -g mintlify
cd business/omnicore/omnicore_agent/docs
mintlify deploy
