#!/bin/bash
# iNavKit SDK - Development and Testing Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🚁 MSPKit SDK - $1${NC}"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        print_error "Python not found. Please install Python 3.7+"
        exit 1
    fi
}

# Install dependencies
install_deps() {
    print_header "Installing Dependencies"
    check_python
    
    echo "Installing core dependencies..."
    $PYTHON -m pip install pyserial
    print_success "Dependencies installed"
}

# Install development dependencies
install_dev() {
    print_header "Installing Development Dependencies"
    check_python
    
    echo "Installing development dependencies..."
    $PYTHON -m pip install pytest pytest-cov black isort flake8 mypy
    print_success "Development dependencies installed"
}

# Run installation test
test() {
    print_header "Running Installation Test"
    check_python
    
    $PYTHON test_installation.py
}

# Run the comprehensive demo
demo() {
    print_header "Running Comprehensive Demo"
    check_python
    
    if [ "$1" = "--interactive" ]; then
        $PYTHON examples/comprehensive_demo.py --interactive
    else
        $PYTHON examples/comprehensive_demo.py
    fi
}

# Install the package in development mode
install() {
    print_header "Installing MSPKit SDK"
    check_python
    
    $PYTHON -m pip install -e .
    print_success "MSPKit SDK installed in development mode"
}

# Format code
format() {
    print_header "Formatting Code"
    
    if command -v black &> /dev/null; then
        echo "Formatting with black..."
        black mspkit/ examples/ test_installation.py
    else
        print_warning "black not installed. Run 'install-dev' first."
    fi
    
    if command -v isort &> /dev/null; then
        echo "Sorting imports with isort..."
        isort mspkit/ examples/ test_installation.py
    else
        print_warning "isort not installed. Run 'install-dev' first."
    fi
    
    print_success "Code formatted"
}

# Lint code
lint() {
    print_header "Linting Code"
    
    if command -v flake8 &> /dev/null; then
        echo "Linting with flake8..."
        flake8 mspkit/ examples/ test_installation.py --max-line-length=100 --ignore=E203,W503
    else
        print_warning "flake8 not installed. Run 'install-dev' first."
    fi
    
    if command -v mypy &> /dev/null; then
        echo "Type checking with mypy..."
        mypy mspkit/ --ignore-missing-imports
    else
        print_warning "mypy not installed. Run 'install-dev' first."
    fi
    
    print_success "Linting completed"
}

# Run tests
test_full() {
    print_header "Running Full Test Suite"
    
    if command -v pytest &> /dev/null; then
        pytest tests/ -v --cov=mspkit
    else
        print_warning "pytest not installed. Running basic test..."
        test
    fi
}

# Clean up build artifacts
clean() {
    print_header "Cleaning Build Artifacts"
    
    echo "Removing build directories..."
    rm -rf build/ dist/ *.egg-info/
    
    echo "Removing Python cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Build package
build() {
    print_header "Building Package"
    check_python
    
    # Clean first
    clean
    
    echo "Building source distribution..."
    $PYTHON setup.py sdist
    
    echo "Building wheel..."
    $PYTHON setup.py bdist_wheel
    
    print_success "Package built successfully"
    echo "Built files:"
    ls -la dist/
}

# Show help
help() {
    print_header "Available Commands"
    
    echo "Setup and Installation:"
    echo "  install-deps     Install core dependencies (pyserial)"
    echo "  install-dev      Install development dependencies"
    echo "  install          Install iNavKit SDK in development mode"
    echo ""
    echo "Testing and Validation:"
    echo "  test             Run installation test"
    echo "  test-full        Run full test suite (requires pytest)"
    echo "  demo             Run comprehensive demo"
    echo "  demo --interactive  Run interactive demo"
    echo ""
    echo "Development:"
    echo "  format           Format code with black and isort"
    echo "  lint             Lint code with flake8 and mypy"
    echo "  clean            Clean build artifacts"
    echo "  build            Build distribution packages"
    echo ""
    echo "Usage: ./scripts.sh <command>"
}

# Main script logic
case "$1" in
    "install-deps")
        install_deps
        ;;
    "install-dev")
        install_dev
        ;;
    "install")
        install
        ;;
    "test")
        test
        ;;
    "test-full")
        test_full
        ;;
    "demo")
        shift
        demo "$@"
        ;;
    "format")
        format
        ;;
    "lint")
        lint
        ;;
    "clean")
        clean
        ;;
    "build")
        build
        ;;
    "help"|"--help"|"-h"|"")
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
