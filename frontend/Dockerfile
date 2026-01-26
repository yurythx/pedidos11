FROM node:20-alpine

# Diretório de trabalho
WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código
COPY . .

# Build para produção (opcional)
# RUN npm run build

# Expor porta
EXPOSE 3000

# Comando de desenvolvimento
CMD ["npm", "run", "dev"]
