# Use a imagem oficial Python 3.11 slim como base
FROM python:3.11-slim

# Instalar dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    unzip \
    xvfb \
    libnss3 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libdrm2 \
    libgbm1 \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Criar um diretório de trabalho para a aplicação
WORKDIR /app

# Copiar apenas requirements.txt primeiro para alavancar caching
COPY requirements.txt ./

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar o pacote browser-use e suas funcionalidades
RUN pip install browser-use
RUN pip install "browser-use[memory]"

# Instalar o Playwright e os browsers
RUN playwright install chromium --with-deps

# Install Playwright and browsers with system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium
RUN playwright install-deps

# Copiar todo o código da aplicação para dentro do contêiner
COPY . .

# Expor porta relevante
EXPOSE 9090

# Definir variável de ambiente
ENV PYTHONUNBUFFERED=1

# Executar o server.py, ajuste conforme a necessidade da sua aplicação
CMD ["python", "server.py"]