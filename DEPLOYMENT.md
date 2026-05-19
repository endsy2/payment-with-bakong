# VPS Deployment Guide - Payment with Bakong

This guide covers deploying your FastAPI application with Bakong KHQR integration on a VPS.

## Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Domain name (optional but recommended)
- Node.js backend running (for payment insertion endpoint)

## 1. Initial VPS Setup

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip nginx git curl
```

### Create Application User
```bash
sudo adduser --disabled-password --gecos "" appuser
sudo usermod -aG sudo appuser
```

## 2. Application Deployment

### Switch to Application User
```bash
sudo su - appuser
```

### Clone Repository
```bash
cd ~
git clone <your-repository-url> payment-with-bakong
cd payment-with-bakong
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure Environment Variables
```bash
nano .env
```

Update with production values:
```env
token=your_bakong_api_token_here
```

**Important**: Make sure your Node.js backend is running and accessible at `http://127.0.0.1:3000` (or update the `BASE_URL` in `app/service/BakongService.py` if different).

### Test Application
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Press `Ctrl+C` to stop after verifying it works.

## 3. Systemd Service Setup

Exit to root/sudo user:
```bash
exit
```

### Create Systemd Service File
```bash
sudo nano /etc/systemd/system/payment-bakong.service
```

Add the following content:
```ini
[Unit]
Description=Payment with Bakong FastAPI Application
After=network.target

[Service]
Type=simple
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/payment-with-bakong
Environment="PATH=/home/appuser/payment-with-bakong/venv/bin:/usr/bin"
ExecStart=/home/appuser/payment-with-bakong/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable payment-bakong
sudo systemctl start payment-bakong
sudo systemctl status payment-bakong
```

## 4. Nginx Reverse Proxy Setup

### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/payment-bakong
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or VPS IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/payment-bakong /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. SSL Certificate (Optional but Recommended)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts. Certbot will automatically configure Nginx for HTTPS.

### Auto-renewal
```bash
sudo systemctl status certbot.timer
```

## 6. Firewall Configuration

### Configure UFW
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 7. Monitoring and Logs

### View Application Logs
```bash
sudo journalctl -u payment-bakong -f
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Check Service Status
```bash
sudo systemctl status payment-bakong
sudo systemctl status nginx
```

## 8. Updating the Application

```bash
sudo su - appuser
cd ~/payment-with-bakong
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
exit
sudo systemctl restart payment-bakong
```

## 9. Environment Configuration Notes

### Node.js Backend Connection
Your FastAPI app connects to a Node.js backend at `http://127.0.0.1:3000`. Make sure:

1. Node.js backend is running on the same VPS
2. The endpoint `/payment/insertPayment` is accessible
3. Update `BASE_URL` in `app/service/BakongService.py` if your Node.js backend runs on a different host/port

### Bakong API Token
- Get your token from [Bakong Developer Portal](https://bakong.nbc.gov.kh/)
- Store it securely in `.env` file
- Never commit the token to version control

## 10. Troubleshooting

### Service Won't Start
```bash
sudo journalctl -u payment-bakong -n 50
```

### Node.js Backend Connection Issues
```bash
# Check if Node.js backend is running
curl http://127.0.0.1:3000/health  # or appropriate endpoint
# Check logs for connection errors
sudo journalctl -u payment-bakong -f | grep "Node.js"
```

### Bakong API Issues
```bash
# Check if token is loaded correctly
sudo journalctl -u payment-bakong -f | grep "token"
# Verify .env file exists and has correct permissions
ls -la /home/appuser/payment-with-bakong/.env
```

### Port Already in Use
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Permission Issues
```bash
sudo chown -R appuser:appuser /home/appuser/payment-with-bakong
```

## Security Recommendations

1. **Secure Bakong Token** - Never commit to git, set proper permissions: `chmod 600 .env`
2. **Change default passwords** - Update system user passwords
3. **Regular updates** - Keep system and dependencies updated
4. **Monitor logs** - Regularly check application and system logs
5. **Use HTTPS** - Always use SSL certificates in production
6. **Limit SSH access** - Use SSH keys instead of passwords
7. **Configure fail2ban** - Protect against brute force attacks
8. **Secure Node.js backend** - Ensure proper authentication between services

## Performance Tuning

### Adjust Workers
Edit systemd service to change worker count based on CPU cores:
```bash
--workers 4  # Formula: (2 x CPU cores) + 1
```

### Connection Pooling
For better performance with Node.js backend calls, consider implementing connection pooling in your httpx client.

## Support

For issues related to:
- **Bakong KHQR**: Check [Bakong documentation](https://bakong.nbc.gov.kh/)
- **FastAPI**: Visit [FastAPI docs](https://fastapi.tiangolo.com/)
- **Application issues**: Check application logs

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**VPS Provider**: _____________  
**Domain**: _____________
