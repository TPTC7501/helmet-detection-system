# Deployment Guide - Production Deployment

## System Requirements

### Minimum
- Windows 10 / Linux (Ubuntu 20.04+)
- 4GB RAM
- 10GB SSD storage
- USB 3.0 or Gigabit Ethernet (for camera)

### Recommended
- NVIDIA GPU (GeForce GTX 1050 Ti or better)
- 8GB+ RAM
- 20GB+ SSD storage
- Dedicated network segment for cameras

---

## Windows Deployment

### Step 1: Install Dependencies

```batch
install.bat
```

This will:
- Create Python virtual environment
- Install all Python packages
- Download YOLO models (~140MB)
- Initialize SQLite database

### Step 2: Configure System

Edit `config.yaml`:

```yaml
camera:
  source: 'rtsp://admin:password@192.168.1.100:554/stream'
  fps: 30
  frame_width: 1280
  frame_height: 720
  reconnect_interval: 5

detection:
  person_confidence: 0.5
  helmet_confidence: 0.6

server:
  port: 8000
  debug: false

logging:
  level: 'INFO'
  file: 'logs/helmet_detection.log'
```

### Step 3: Start Backend

```batch
run.bat
```

Backend will start at: http://localhost:8000

### Step 4: Access Dashboard

- **Web**: http://localhost:8000/dashboard
- **API**: http://localhost:8000/api/events
- **Health**: http://localhost:8000/health

---

## Docker Deployment (Optional)

### Build Image

```bash
docker build -t helmet-detection:1.0 .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/evidence:/app/evidence \
  --gpus all \
  helmet-detection:1.0
```

---

## Performance Tuning

### For CPU-Only Systems

```yaml
detection:
  yolo_size: 'nano'  # Smallest model
  frame_skip: 3      # Process every 3rd frame

models:
  device: 'cpu'

performance:
  worker_threads: 1
```

### For GPU Systems

```yaml
detection:
  yolo_size: 'small'  # Balanced model
  frame_skip: 1       # Process all frames

models:
  device: 'gpu'
  use_tensorrt: true  # NVIDIA acceleration

performance:
  worker_threads: 4
```

---

## Monitoring & Logging

### Check Logs

```bash
tail -f logs/helmet_detection.log
```

### Monitor System

```bash
python tools/health_check.py
```

Expected output:
```
System Health Report
====================
Camera Status: CONNECTED
Database: OK
GPU Memory: 2048/4096 MB
CPU Usage: 45%
Memory Usage: 2.1 GB / 8 GB
```

---

## Automated Startup (Windows)

### Create Scheduled Task

1. Open Task Scheduler
2. Create Basic Task → "Helmet Detection"
3. Trigger: "At startup"
4. Action: Start program
   - Program: `run.bat`
   - Start in: `C:\path\to\helmet-detection-system`

### Or use Batch File

Create `autostart.bat`:
```batch
@echo off
cd C:\path\to\helmet-detection-system
start run.bat
```

---

## Database Backup

### Backup Events

```bash
SQLLite> .backup helmet_detection_backup.db helmet_detection.db
```

### Restore from Backup

```bash
SQLLite> .backup helmet_detection.db helmet_detection_backup.db
```

---

## API Integration

### Webhook for Violations

Configure in `config.yaml`:

```yaml
notifications:
  enabled: true
  webhook_url: 'https://your-server.com/api/violations'
```

Backend will POST on violation:

```json
{
  "timestamp": "2026-09-12T10:30:45.123Z",
  "track_id": 5,
  "frame_number": 1200,
  "detection_type": "no_helmet",
  "confidence": 0.87,
  "bbox": [245, 120, 380, 400],
  "camera_source": "entrance"
}
```

---

## Firewall Configuration

### Allow Dashboard Access

```bash
netsh advfirewall firewall add rule name="Helmet Detection" dir=in action=allow protocol=tcp localport=8000
```

### Allow RTSP Cameras

```bash
netsh advfirewall firewall add rule name="RTSP" dir=out action=allow protocol=tcp remoteport=554
```

---

## Security Best Practices

1. **API Authentication** (Future)
   - Use API keys for `/api/` endpoints
   - Store credentials in environment variables

2. **HTTPS** (Reverse Proxy)
   - Use Nginx/Apache as reverse proxy
   - Enable SSL/TLS certificates

3. **Database Encryption**
   - Enable SQLite encryption (SQLCipher)
   - Backup to secure location

4. **Access Control**
   - Restrict dashboard to trusted networks
   - Use VPN for remote access

---

## Support & Troubleshooting

See `TROUBLESHOOTING.md` for:
- Common issues and solutions
- Performance optimization
- Error message reference

---

**Version**: 1.0.0 | **Last Updated**: 2026-09-12
