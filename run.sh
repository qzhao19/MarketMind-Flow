#!/bin/bash

# Project configuration
PROJECT_NAME="marketflow-venv"
PYTHON_VERSION="3.11.11"  # Specify Python version
REQUIREMENTS_FILE="requirements.txt"  # Dependencies file path

# Check if already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" || "$CONDA_PREFIX" != "" ]]; then
    echo "⚠️  Detected an active virtual environment. Please deactivate first."
    exit 1
fi

# Try creating conda environment (if conda is available)
if command -v conda &> /dev/null; then
    echo "🐍 Detected conda, creating conda environment..."
    conda create -n $PROJECT_NAME python=$PYTHON_VERSION -y
    if [ $? -eq 0 ]; then
        echo "✅ Conda environment created successfully"
        echo "🔧 Activate with: conda activate $PROJECT_NAME"
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate $PROJECT_NAME
    else
        echo "❌ Conda environment creation failed, falling back to venv"
    fi
fi

# Fallback to venv if conda not available or failed
if [[ "$CONDA_PREFIX" == "" && "$VIRTUAL_ENV" == "" ]]; then
    echo "🐍 Creating virtual environment with venv..."
    python -m venv ./venv_$PROJECT_NAME
    if [ $? -eq 0 ]; then
        echo "✅ venv environment created successfully"
        echo "🔧 Activate with: source ./venv_$PROJECT_NAME/bin/activate"
        source ./venv_$PROJECT_NAME/bin/activate
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Verify pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please ensure Python is installed correctly."
    exit 1
fi

# Upgrade pip
echo "🛠️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "📦 Installing dependencies ($REQUIREMENTS_FILE)..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "⚠️  $REQUIREMENTS_FILE not found, skipping dependency installation"
fi

echo -e "\n🎉 Environment setup complete!"
echo "👉 For future usage, activate the environment with:"
if [[ "$CONDA_PREFIX" != "" ]]; then
    echo "    conda activate $PROJECT_NAME"
else
    echo "    source ./venv_$PROJECT_NAME/bin/activate"
fi

echo -e "\n🛠️  Current environment info:"
python --version
pip --version