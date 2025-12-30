# Cloudflare Tunnel + aaPanel

## Cenário
- Servir a API atrás de Cloudflare Tunnel usando um servidor com aaPanel.
- TLS é gerenciado pela Cloudflare; o backend escuta em 8000.

## Passos com Cloudflared
1. Instalar cloudflared no servidor (Ubuntu/Debian):
```bash
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
```
2. Login e criar túnel:
```bash
cloudflared tunnel login
cloudflared tunnel create pedidos11
```
3. Configurar hostname público e apontar para o backend:
Crie `~/.cloudflared/config.yml`:
```yaml
tunnel: pedidos11
credentials-file: /root/.cloudflared/<id>.json
ingress:
  - hostname: seu.dominio.com
    service: http://localhost:8000
  - service: http_status:404
```
4. Iniciar como serviço:
```bash
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
```

## Subir containers
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## Configuração do Django para proxy
- Ambiente:
  - USE_X_FORWARDED_HOST=True
  - USE_PROXY_SSL_HEADER=True
  - CSRF_TRUSTED_ORIGINS=https://seu.dominio.com
  - ALLOWED_HOSTS=seu.dominio.com
- Resultado:
  - Django respeita o Host/X-Forwarded-* e considera requisições como HTTPS.

## Alternativa com Nginx (aaPanel)
- Crie um site Nginx que faça proxy para `http://127.0.0.1:8000`:
```
location / {
  proxy_pass http://127.0.0.1:8000;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```
- No Cloudflare Tunnel, aponte `service: http://localhost:80`.
- Mantenha as variáveis de proxy em Django como acima.

## Verificação
- Acesse `https://seu.dominio.com/api/health/`
- Swagger: `https://seu.dominio.com/api/docs/`
- Redoc: `https://seu.dominio.com/api/redoc/`
