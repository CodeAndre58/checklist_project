#!/bin/bash

# =============================================================================
# PRISMA 2020 Analyzer - Quick Setup & First Run Script
# =============================================================================

echo "🚀 PRISMA 2020 Scoping Review Analyzer - Setup Script"
echo "========================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify Python
echo -e "${BLUE}1. Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.10+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
echo ""

# Step 2: Activate venv
echo -e "${BLUE}2. Activating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    echo "   Creating venv..."
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Step 3: Install dependencies
echo -e "${BLUE}3. Installing dependencies...${NC}"
pip install -e . > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Step 4: Run tests
echo -e "${BLUE}4. Running verification tests...${NC}"
python3 tests/test_imports.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All imports verified"
else
    echo "❌ Import test failed"
    exit 1
fi
echo ""

# Step 5: Show next steps
echo -e "${YELLOW}✅ Setup Complete!${NC}"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1. Start Ollama in another terminal:"
echo "   ${BLUE}ollama serve${NC}"
echo ""
echo "2. In a third terminal, download the model (one-time):"
echo "   ${BLUE}ollama pull gemma4:31b-cloud${NC}"
echo ""
echo "3. Run the demo (requires Ollama running):"
echo "   ${BLUE}python3 tests/demo.py${NC}"
echo ""
echo "4. Analyze your first PDF:"
echo "   ${BLUE}python3 cli.py /path/to/your_paper.pdf${NC}"
echo ""
echo "📚 Documentation:"
echo "   - QUICKSTART.md  - Fast start guide"
echo "   - README_FULL.md - Complete documentation"
echo "   - SETUP.md       - Detailed installation"
echo ""
echo "🧪 Available tests:"
echo "   python3 tests/test_pdf_processor.py"
echo "   python3 tests/test_imports.py"
echo "   python3 tests/demo.py"
echo ""
