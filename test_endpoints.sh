#!/bin/bash

# Base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing CounselBot API endpoints..."
echo "-----------------------------------"

# Test 1: Health Check
echo -e "\n${GREEN}Testing Health Check Endpoint${NC}"
curl -s "${BASE_URL}/health" | jq '.'

# Test 2: Root Endpoint
echo -e "\n${GREEN}Testing Root Endpoint${NC}"
curl -s "${BASE_URL}/" | jq '.'

# Test 3: Sentiment Analysis
echo -e "\n${GREEN}Testing Sentiment Analysis Endpoint${NC}"
curl -s -X POST "${BASE_URL}/analyze/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I am feeling very happy today!"}' | jq '.'

# Test 4: Mental Health Analysis
echo -e "\n${GREEN}Testing Mental Health Analysis Endpoint${NC}"
curl -s -X POST "${BASE_URL}/analyze/mental-health" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I have been feeling anxious and stressed lately."}' | jq '.'

# Test 5: Counsel Generation
echo -e "\n${GREEN}Testing Counsel Generation Endpoint${NC}"
curl -s -X POST "${BASE_URL}/generate/counsel" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I am feeling overwhelmed with work and personal life."}' | jq '.'

# Test 6: All Analysis
echo -e "\n${GREEN}Testing All Analysis Endpoint${NC}"
curl -s -X POST "${BASE_URL}/analyze/all" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I have been having trouble sleeping and feel constantly tired."}' | jq '.'

# Test 7: Clear History and New Counsel
echo -e "\n${GREEN}Testing Clear History and New Counsel${NC}"
curl -s -X POST "${BASE_URL}/generate/counsel" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I need to start fresh.", "clear_history": true}' | jq '.'

echo -e "\n-----------------------------------"
echo "All tests completed!" 