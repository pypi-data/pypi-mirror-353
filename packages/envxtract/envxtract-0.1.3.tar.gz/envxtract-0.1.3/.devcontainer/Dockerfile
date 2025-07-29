# Use Python 3.13 to match pyproject.toml requirement
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential build tools
    build-essential \
    gcc \
    g++ \
    make \
    # Version control and networking
    git \
    curl \
    wget \
    ca-certificates \
    # File operations and compression
    zip \
    unzip \
    tar \
    gzip \
    bzip2 \
    xz-utils \
    # System utilities
    tree \
    htop \
    nano \
    vim \
    # SSH and networking tools
    openssh-client \
    rsync \
    # Process and network monitoring
    procps \
    lsof \
    net-tools \
    # GPG for security
    gnupg2 \
    # Dependencies for geospatial libraries
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    # For matplotlib and other plotting libraries
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    # For netCDF files
    libnetcdf-dev \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Node.js and npm for JavaScript development
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g eslint \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install gh -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management (system-wide)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && chmod +x /usr/local/bin/uv

# Create a non-root user with sudo capabilities
RUN useradd -m -s /bin/bash -u 1000 vscode \
    && apt-get update \
    && apt-get install -y sudo \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Change ownership of workspace to vscode user
RUN chown -R vscode:vscode /workspace

# Switch to non-root user
USER vscode

# Set up uv for the vscode user
ENV PATH="/home/vscode/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files from workspace root
COPY --chown=vscode:vscode pyproject.toml uv.lock* ./

# Create initialization script that handles virtual environment properly
RUN echo '#!/bin/bash\n\
    set -e\n\
    \n\
    echo "Setting up Python environment..."\n\
    \n\
    # Remove any existing invalid .venv directory\n\
    if [ -d "/workspace/.venv" ] && [ ! -f "/workspace/.venv/bin/python" ]; then\n\
    echo "Removing invalid virtual environment..."\n\
    rm -rf /workspace/.venv\n\
    fi\n\
    \n\
    # Create or sync virtual environment\n\
    if [ ! -f "/workspace/.venv/bin/python" ]; then\n\
    echo "Creating new virtual environment..."\n\
    uv sync --dev\n\
    echo "Virtual environment created successfully!"\n\
    else\n\
    echo "Virtual environment exists, syncing dependencies..."\n\
    uv sync --dev\n\
    echo "Dependencies synced successfully!"\n\
    fi\n\
    \n\
    # Verify the virtual environment\n\
    if [ -f "/workspace/.venv/bin/python" ]; then\n\
    echo "Python version: $(/workspace/.venv/bin/python --version)"\n\
    echo "uv version: $(uv --version)"\n\
    echo "Virtual environment is ready!"\n\
    else\n\
    echo "ERROR: Failed to create virtual environment"\n\
    exit 1\n\
    fi\n\
    ' > /home/vscode/init-env.sh && chmod +x /home/vscode/init-env.sh

# Create a .bashrc that automatically activates the virtual environment
RUN echo '\n\
    # Auto-activate virtual environment if it exists\n\
    if [ -f "/workspace/.venv/bin/activate" ]; then\n\
    source /workspace/.venv/bin/activate\n\
    export VIRTUAL_ENV="/workspace/.venv"\n\
    export PATH="/workspace/.venv/bin:$PATH"\n\
    fi\n\
    \n\
    # Add workspace to Python path\n\
    export PYTHONPATH="/workspace:$PYTHONPATH"\n\
    \n\
    # uv cache directory\n\
    export UV_CACHE_DIR="/workspace/.uv-cache"\n\
    ' >> /home/vscode/.bashrc

# Set environment variables
ENV VIRTUAL_ENV=".venv" \
    PATH="/workspace/.venv/bin:${PATH}" \
    PYTHONPATH="/workspace" \
    UV_CACHE_DIR="/workspace/.uv-cache"

# Expose common development ports
EXPOSE 8000 8080 3000 5000

# Default command
CMD ["/bin/bash"]