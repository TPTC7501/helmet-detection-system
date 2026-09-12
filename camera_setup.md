# Camera Setup Guide

## USB Camera Setup

### Windows

1. **Connect USB camera to computer**
2. **Verify in Device Manager**
   - Right-click Start → Device Manager
   - Look under "Imaging devices"
   - Camera should appear as "USB Video Device"

3. **Update config.yaml**
   ```yaml
   camera:
     source: 0  # 0 for first USB camera, 1 for second, etc.
   ```

4. **Test connection**
   ```bash
   python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED')"
   ```

---

## RTSP Camera Setup

### Configuration

1. **Get camera RTSP URL**
   - Access camera web interface (usually http://camera-ip)
   - Find RTSP stream URL in network settings
   - Format: `rtsp://username:password@camera-ip:554/stream`

2. **Update config.yaml**
   ```yaml
   camera:
     source: 'rtsp://admin:password@192.168.1.100:554/stream'
     reconnect_interval: 5
     reconnect_max_attempts: 10
   ```

3. **Test connection**
   ```bash
   python tools/test_camera.py --url "rtsp://...."
   ```

### Common Camera URLs

**Hikvision:**
```
rtsp://username:password@ip:554/Streaming/Channels/101
```

**Dahua:**
```
rtsp://username:password@ip:554/stream/main
```

**Axis:**
```
rtsp://username:password@ip:554/axis-media/media.amp
```

**Generic IP Camera:**
```
rtsp://username:password@ip:554/stream
```

---

## Multi-Camera Setup

### Configuration for 2+ Cameras

```yaml
cameras:
  - name: "entrance"
    source: "rtsp://admin:pass@192.168.1.100/stream"
    
  - name: "warehouse"
    source: "rtsp://admin:pass@192.168.1.101/stream"
    
  - name: "dock"
    source: 0  # USB camera
```

### Running with Multiple Cameras

```bash
python backend/app.py --config config_multi.yaml
```

---

## Troubleshooting

### Camera Not Detected
- **USB**: Reinstall camera driver, try different USB port
- **RTSP**: Verify network connectivity, check firewall rules
- **Check URL**: Use VLC to test RTSP URL first

### Slow FPS
- Reduce frame resolution in config
- Increase `frame_skip` parameter
- Use newer GPU with CUDA support

### Connection Drops
- Increase `reconnect_max_attempts`
- Check network cable/WiFi signal
- Consider using wired connection for RTSP

---

**Version**: 1.0.0
