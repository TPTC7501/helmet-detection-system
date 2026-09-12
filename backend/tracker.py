"""Centroid-based tracking for person tracking."""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Track:
    """Single track object."""
    
    def __init__(self, track_id: int, detection):
        self.id = track_id
        self.bbox = (detection.x1, detection.y1, detection.x2, detection.y2)
        self.centroid = (detection.centroid_x, detection.centroid_y)
        self.confidence = detection.confidence
        self.frames_since_update = 0
        self.total_frames = 1
        self.history = [self.centroid]
    
    def update(self, detection):
        """Update track with new detection."""
        self.bbox = (detection.x1, detection.y1, detection.x2, detection.y2)
        self.centroid = (detection.centroid_x, detection.centroid_y)
        self.confidence = detection.confidence
        self.frames_since_update = 0
        self.total_frames += 1
        self.history.append(self.centroid)
        if len(self.history) > 30:
            self.history.pop(0)
    
    def increment_missing(self):
        """Increment missing frame counter."""
        self.frames_since_update += 1
    
    def distance_to(self, centroid: Tuple[float, float]) -> float:
        """Euclidean distance to centroid."""
        dx = self.centroid[0] - centroid[0]
        dy = self.centroid[1] - centroid[1]
        return np.sqrt(dx**2 + dy**2)


class CentroidTracker:
    """Centroid-based object tracker."""
    
    def __init__(self, max_missing_frames: int = 30, max_centroid_distance: int = 50):
        """
        Initialize tracker.
        
        Args:
            max_missing_frames: Remove track if not seen for this many frames
            max_centroid_distance: Max distance (pixels) to match detections
        """
        self.next_id = 0
        self.tracks = OrderedDict()
        self.max_missing_frames = max_missing_frames
        self.max_centroid_distance = max_centroid_distance
        logger.info(f"CentroidTracker initialized (max_missing={max_missing_frames}, max_dist={max_centroid_distance})")
    
    def update(self, detections: List) -> Dict[int, Tuple]:
        """Update tracks with new detections."""
        if len(detections) == 0:
            for track_id in list(self.tracks.keys()):
                self.tracks[track_id].increment_missing()
            self._cleanup_tracks()
            return {}
        
        input_centroids = np.array([(d.centroid_x, d.centroid_y) for d in detections])
        
        if len(self.tracks) == 0:
            for detection in detections:
                self._register_track(detection)
            return self._get_tracked_detections(detections)
        
        tracked_ids = list(self.tracks.keys())
        track_centroids = np.array([self.tracks[tid].centroid for tid in tracked_ids])
        
        distances = np.zeros((len(tracked_ids), len(detections)))
        for i, track_id in enumerate(tracked_ids):
            for j, detection in enumerate(detections):
                distances[i, j] = self.tracks[track_id].distance_to((detection.centroid_x, detection.centroid_y))
        
        matched_tracks = set()
        matched_detections = set()
        
        matches = []
        for i, j in sorted(
            [(i, j) for i in range(len(tracked_ids)) for j in range(len(detections))],
            key=lambda x: distances[x[0], x[1]]
        ):
            if distances[i, j] < self.max_centroid_distance:
                if i not in matched_tracks and j not in matched_detections:
                    matches.append((i, j))
                    matched_tracks.add(i)
                    matched_detections.add(j)
        
        for i, j in matches:
            track_id = tracked_ids[i]
            self.tracks[track_id].update(detections[j])
        
        for i, track_id in enumerate(tracked_ids):
            if i not in matched_tracks:
                self.tracks[track_id].increment_missing()
        
        for j, detection in enumerate(detections):
            if j not in matched_detections:
                self._register_track(detection)
        
        self._cleanup_tracks()
        return self._get_tracked_detections(detections)
    
    def _register_track(self, detection):
        """Register new track."""
        track_id = self.next_id
        self.tracks[track_id] = Track(track_id, detection)
        self.next_id += 1
        logger.debug(f"New track registered: {track_id}")
    
    def _cleanup_tracks(self):
        """Remove old tracks."""
        to_remove = [tid for tid, track in self.tracks.items() if track.frames_since_update > self.max_missing_frames]
        for tid in to_remove:
            del self.tracks[tid]
            logger.debug(f"Track removed: {tid}")
    
    def _get_tracked_detections(self, detections: List) -> Dict[int, Tuple]:
        """Get active tracks."""
        result = {}
        for track_id, track in self.tracks.items():
            if track.frames_since_update == 0:
                result[track_id] = track.bbox
        return result
    
    def get_all_tracks(self) -> Dict[int, Track]:
        """Get all active tracks."""
        return self.tracks
    
    def get_track(self, track_id: int) -> Optional[Track]:
        """Get specific track."""
        return self.tracks.get(track_id)
