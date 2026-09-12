"""FastAPI backend application."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pathlib import Path
from datetime import datetime, timedelta
import json
import csv
import io
import logging
from typing import List

from backend.database import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Helmet Detection System",
    description="Real-time helmet detection for construction sites",
    version="1.0.0"
)

# Initialize database
db = Database()

# Static files
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# ============================================================================
# DASHBOARD & UI
# ============================================================================

@app.get("/dashboard")
async def dashboard():
    """Serve main dashboard HTML."""
    dashboard_path = Path("frontend/dashboard.html")
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    else:
        return {"message": "Dashboard not found. Create frontend/dashboard.html"}


# ============================================================================
# API ENDPOINTS - EVENTS
# ============================================================================

@app.get("/api/events")
async def get_events(limit: int = 100, detection_type: str = None):
    """
    Get recent events.
    
    Query parameters:
    - limit: Number of events to return (default: 100)
    - detection_type: Filter by 'helmet' or 'no_helmet' (optional)
    """
    try:
        events = db.get_events(detection_type=detection_type)
        
        # Format events for JSON
        result = []
        for event in events[-limit:]:
            result.append({
                'id': event['id'],
                'timestamp': event['timestamp'],
                'frame_number': event['frame_number'],
                'track_id': event['track_id'],
                'detection_type': event['detection_type'],
                'confidence': event['confidence'],
                'bbox': {
                    'x1': event['bbox_x1'],
                    'y1': event['bbox_y1'],
                    'x2': event['bbox_x2'],
                    'y2': event['bbox_y2']
                },
                'evidence_image': event['evidence_image_path'],
                'camera_source': event['camera_source']
            })
        
        return {'events': result, 'count': len(result)}
    
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/count")
async def get_event_count(detection_type: str = None):
    """Get event count by type."""
    try:
        total = db.get_event_count()
        helmet_count = db.get_event_count('helmet')
        no_helmet_count = db.get_event_count('no_helmet')
        
        return {
            'total': total,
            'helmet': helmet_count,
            'no_helmet': no_helmet_count
        }
    except Exception as e:
        logger.error(f"Error counting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API ENDPOINTS - STATISTICS & ANALYTICS
# ============================================================================

@app.get("/api/stats")
async def get_statistics():
    """Get latest statistics."""
    try:
        stats = db.get_statistics(limit=1)
        if stats:
            stat = stats[0]
            return {
                'session_start': stat['session_start'],
                'total_frames': stat['total_frames'],
                'total_unique_persons': stat['total_unique_persons'],
                'helmet_count': stat['helmet_count'],
                'no_helmet_count': stat['no_helmet_count'],
                'compliance_rate': stat['helmet_count'] / max(1, stat['helmet_count'] + stat['no_helmet_count']),
                'avg_confidence': stat['avg_confidence'],
                'processing_time_ms': stat['processing_time_ms']
            }
        else:
            return {
                'session_start': None,
                'total_frames': 0,
                'total_unique_persons': 0,
                'helmet_count': 0,
                'no_helmet_count': 0,
                'compliance_rate': 0,
                'avg_confidence': 0,
                'processing_time_ms': 0
            }
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API ENDPOINTS - REPORTS & EXPORTS
# ============================================================================

@app.get("/api/report/csv")
async def export_csv():
    """Export events as CSV."""
    try:
        events = db.get_events()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['id', 'timestamp', 'frame_number', 'track_id', 'detection_type', 
                        'confidence', 'bbox_x1', 'bbox_y1', 'bbox_x2', 'bbox_y2', 
                        'evidence_image', 'camera_source'])
        
        # Data
        for event in events:
            writer.writerow([
                event['id'],
                event['timestamp'],
                event['frame_number'],
                event['track_id'],
                event['detection_type'],
                event['confidence'],
                event['bbox_x1'],
                event['bbox_y1'],
                event['bbox_x2'],
                event['bbox_y2'],
                event['evidence_image_path'],
                event['camera_source']
            ])
        
        # Return as streaming response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=events.csv"}
        )
    
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/stats")
async def export_statistics():
    """Export statistics as JSON."""
    try:
        stats = db.get_statistics(limit=1)
        
        if stats:
            stat = stats[0]
            data = {
                'session_start': stat['session_start'],
                'total_frames': stat['total_frames'],
                'total_unique_persons': stat['total_unique_persons'],
                'helmet_count': stat['helmet_count'],
                'no_helmet_count': stat['no_helmet_count'],
                'compliance_rate': stat['helmet_count'] / max(1, stat['helmet_count'] + stat['no_helmet_count']),
                'avg_confidence': stat['avg_confidence'],
                'processing_time_ms': stat['processing_time_ms'],
                'export_time': datetime.now().isoformat()
            }
        else:
            data = {'message': 'No statistics available'}
        
        return data
    
    except Exception as e:
        logger.error(f"Error exporting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API ENDPOINTS - HEALTH & STATUS
# ============================================================================

@app.get("/health")
async def health_check():
    """System health check endpoint."""
    try:
        # Check database
        db_ok = True
        try:
            count = db.get_event_count()
        except Exception:
            db_ok = False
        
        return {
            'status': 'healthy' if db_ok else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if db_ok else 'disconnected',
            'camera': 'unknown',
            'uptime_seconds': 0
        }
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    # Load from config.yaml
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.warning(f"Could not load config: {e}")
        return {"message": "Config not available"}


# ============================================================================
# ROOT & INFO
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        'name': 'Helmet Detection System',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'dashboard': '/dashboard',
            'events': '/api/events',
            'stats': '/api/stats',
            'export_csv': '/api/report/csv',
            'export_json': '/api/report/stats',
            'health': '/health',
            'config': '/api/config'
        }
    }


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    db.close()
    logger.info("Backend shutdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
