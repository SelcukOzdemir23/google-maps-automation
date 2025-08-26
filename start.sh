#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo " Google Maps Business Scraper Setup"
echo "========================================"
echo -e "${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed${NC}"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo -e "${GREEN}[INFO] Python found${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[INFO] Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}[INFO] Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}[INFO] Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to install requirements${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p csv_files
mkdir -p custom_searches

echo
echo -e "${GREEN}[SUCCESS] Setup completed!${NC}"
echo -e "${YELLOW}[INFO] Starting application...${NC}"
echo
echo -e "${BLUE}========================================"
echo " Application is starting..."
echo " Open your browser and go to:"
echo " http://localhost:8501"
echo "========================================"
echo -e "${NC}"

# Start the application
streamlit run app.py