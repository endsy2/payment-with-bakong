# VPS Deployment Guide - Payment with Bakong

This guide covers deploying your FastAPI application with Bakong KHQR integration on a VPS.

## Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Node.js backend running on the same VPS (for payment insertion endpoint)

## 1. Initial VPS Setup

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip git curl net-tools
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
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Visit `http://127.0.0.1:8000/docs` to see the API documentation.

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
ExecStart=/home/appuser/payment-with-bakong/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
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

## 4. Firewall Configuration (Optional)

If you want to restrict access to localhost only (recommended for internal use):

```bash
# Only allow SSH access from outside
sudo ufw allow 22/tcp
sudo ufw enable
sudo ufw status
```

**Note**: Port 8000 is bound to `127.0.0.1` (localhost only), so it's not accessible from outside the VPS. Only your Node.js backend running on the same server can access it.

## 5. Monitoring and Logs

### View Application Logs
```bash
sudo journalctl -u payment-bakong -f
```

### Check Service Status
```bash
sudo systemctl status payment-bakong
```

## 6. Updating the Application

```bash
sudo su - appuser
cd ~/payment-with-bakong
git pull origin main
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
exit
sudo systemctl restart payment-bakong
```

Verify the update:
```bash
sudo systemctl status payment-bakong
sudo journalctl -u payment-bakong -n 20
```

## 7. Environment Configuration Notes

### Node.js Backend Connection
Your FastAPI app connects to a Node.js backend at `http://127.0.0.1:3000`. Make sure:

1. Node.js backend is running on the same VPS
2. The endpoint `/payment/insertPayment` is accessible
3. The endpoint `/bakong/renewToken` is implemented (for token renewal feature)
4. Update `BASE_URL` in `app/service/BakongService.py` if your Node.js backend runs on a different host/port

**Required Node.js Endpoints:**
- `POST /payment/insertPayment` - Accepts payment data with Authorization header
- `POST /bakong/renewToken` - Returns `{"token": "your_bakong_token"}` for token renewal

### Bakong API Token
- Get your token from [Bakong Developer Portal](https://bakong.nbc.gov.kh/)
- Store it securely in `.env` file
- Never commit the token to version control
- The app now supports automatic token renewal via Node.js backend
- Token is cached in memory after first load or renewal

### API Endpoints
Your FastAPI application exposes these endpoints:
- `POST /bakong/generateQR` - Generate Bakong QR code (requires: amount, currency, merchant_name)
- `POST /bakong/verifyMD5` - Verify payment status (requires: md5, booking_id, Authorization header)
- `POST /bakong/payment_info` - Get payment information (requires: md5)
- `POST /bakong/renewToken` - Manually renew Bakong token
- `GET /bakong/checkToken` - Check current token status

## 8. Troubleshooting

### Service Won't Start
```bash
sudo journalctl -u payment-bakong -n 50
```

### Check if Application is Running
```bash
# Check if port 8000 is listening
sudo netstat -tlnp | grep 8000
# Or use ss command
sudo ss -tlnp | grep 8000
```

### Node.js Backend Connection Issues
```bash
# Check if Node.js backend is running
curl http://127.0.0.1:3000/health  # or appropriate endpoint
# Check logs for connection errors
sudo journalctl -u payment-bakong -f | grep "Node.js"
# Test token renewal endpoint
curl -X POST http://127.0.0.1:3000/bakong/renewToken
```

### Bakong API Issues
```bash
# Check if token is loaded correctly
sudo journalctl -u payment-bakong -f | grep "token"
# Verify .env file exists and has correct permissions
ls -la /home/appuser/payment-with-bakong/.env
# Test token status via API
curl http://your-vps-ip:8000/bakong/checkToken
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
5. **Limit SSH access** - Use SSH keys instead of passwords
6. **Configure fail2ban** - Protect against brute force attacks
7. **Secure Node.js backend** - Ensure proper authentication between services
8. **Localhost binding** - App is bound to 127.0.0.1, only accessible from same server

## Performance Tuning

### Adjust Workers
Edit systemd service to change worker count based on your needs:
```bash
--workers 2  # For internal use, 2 workers is usually sufficient
```

For higher load, use formula: `(2 x CPU cores) + 1`

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
**Internal Port**: 8000 (localhost only)
