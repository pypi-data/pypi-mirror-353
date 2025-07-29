"""
Laban Movement Analysis (LMA) inspired notation engine.
Computes movement metrics like direction, intensity, and speed from pose keypoints.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .pose_estimation import PoseResult, Keypoint


class Direction(Enum):
    """Movement direction categories."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"  # Note: Not fully implemented with 2D keypoints
    BACKWARD = "backward" # Note: Not fully implemented with 2D keypoints
    STATIONARY = "stationary"


class Intensity(Enum):
    """Movement intensity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Speed(Enum):
    """Movement speed categories."""
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"


@dataclass
class MovementMetrics:
    """LMA-inspired movement metrics for a frame or segment."""
    frame_index: int
    timestamp: Optional[float] = None
    
    # Primary metrics
    direction: Direction = Direction.STATIONARY
    intensity: Intensity = Intensity.LOW
    speed: Speed = Speed.SLOW
    
    # Numeric values
    velocity: float = 0.0  # pixels/second or normalized units
    acceleration: float = 0.0
    
    # Additional qualities
    fluidity: float = 0.0  # 0-1, smoothness of movement
    expansion: float = 0.0  # 0-1, how spread out the pose is
    
    # Raw displacement data
    center_displacement: Optional[Tuple[float, float]] = None
    total_displacement: float = 0.0


class MovementAnalyzer:
    """Analyzes pose sequences to extract LMA-style movement metrics."""
    
    def __init__(self, fps: float = 30.0, 
                 velocity_threshold_slow: float = 0.01, # Normalized units / frame; will be scaled by fps
                 velocity_threshold_fast: float = 0.1,  # Normalized units / frame; will be scaled by fps
                 intensity_accel_threshold: float = 0.05): # Normalized units / frame^2; will be scaled by fps^2 (approx)
        """
        Initialize movement analyzer.
        
        Args:
            fps: Frames per second of the video
            velocity_threshold_slow: Threshold for slow movement (normalized units per second)
            velocity_threshold_fast: Threshold for fast movement (normalized units per second)
            intensity_accel_threshold: Acceleration threshold for intensity (normalized units per second^2)
        """
        self.fps = fps
        self.frame_duration = 1.0 / fps if fps > 0 else 0.0
        self.velocity_threshold_slow = velocity_threshold_slow
        self.velocity_threshold_fast = velocity_threshold_fast
        self.intensity_accel_threshold = intensity_accel_threshold
    
    def analyze_movement(self, pose_sequence: List[List[PoseResult]]) -> List[MovementMetrics]:
        """
        Analyze a sequence of poses to compute movement metrics.
        
        Args:
            pose_sequence: List of pose results per frame. Each inner list can contain
                           multiple PoseResult if multiple people are detected.
            
        Returns:
            List of movement metrics per frame (currently for the first detected person).
        """
        if not pose_sequence:
            return []
        
        metrics = []
        # For multi-person, these would need to be dictionaries mapping person_id to values
        prev_centers = None # Store as {person_id: center_coords} for multi-person
        prev_velocity = None # Store as {person_id: velocity_value} for multi-person
        
        for frame_idx, frame_poses in enumerate(pose_sequence):
            if not frame_poses:
                # No pose detected in this frame
                metrics.append(MovementMetrics(
                    frame_index=frame_idx,
                    timestamp=frame_idx * self.frame_duration if self.frame_duration else None
                ))
                continue
            
            # --- CURRENT: Analyze first person only ---
            # TODO: Extend to multi-person analysis. This would involve iterating
            # through frame_poses and tracking metrics for each person_id.
            pose = frame_poses[0] 
            # --- END CURRENT ---

            if not pose.keypoints: # Ensure pose object has keypoints
                 metrics.append(MovementMetrics(
                    frame_index=frame_idx,
                    timestamp=frame_idx * self.frame_duration if self.frame_duration else None
                ))
                 # Reset for next frame if this person was being tracked
                 prev_centers = None # Or prev_centers.pop(person_id, None)
                 prev_velocity = None # Or prev_velocity.pop(person_id, None)
                 continue

            # Compute body center
            center = self._compute_body_center(pose.keypoints)
            
            # Initialize metrics for this frame
            frame_metrics = MovementMetrics(
                frame_index=frame_idx,
                timestamp=frame_idx * self.frame_duration if self.frame_duration else None
            )
            
            # Displacement, velocity, etc. can only be computed if there's a previous frame's center
            if prev_centers is not None and frame_idx > 0 and self.fps > 0:
                displacement = (
                    center[0] - prev_centers[0],
                    center[1] - prev_centers[1]
                )
                frame_metrics.center_displacement = displacement
                frame_metrics.total_displacement = np.sqrt(
                    displacement[0]**2 + displacement[1]**2
                )
                
                frame_metrics.velocity = frame_metrics.total_displacement * self.fps
                frame_metrics.direction = self._compute_direction(displacement)
                frame_metrics.speed = self._categorize_speed(frame_metrics.velocity)
                
                if prev_velocity is not None:
                    # Acceleration (change in velocity per second)
                    delta_velocity = frame_metrics.velocity - prev_velocity
                    frame_metrics.acceleration = delta_velocity * self.fps # (units/s)/s = units/s^2
                    
                    frame_metrics.intensity = self._compute_intensity(
                        frame_metrics.acceleration,
                        frame_metrics.velocity
                    )
                    frame_metrics.fluidity = self._compute_fluidity(
                        frame_metrics.acceleration
                    )
            
            frame_metrics.expansion = self._compute_expansion(pose.keypoints)
            metrics.append(frame_metrics)
            
            # Update for next iteration (for the currently tracked person)
            prev_centers = center
            prev_velocity = frame_metrics.velocity
        
        metrics = self._smooth_metrics(metrics)
        return metrics
    
    def _compute_body_center(self, keypoints: List[Keypoint]) -> Tuple[float, float]:
        """Compute the center of mass of the body."""
        major_joints = ["left_hip", "right_hip", "left_shoulder", "right_shoulder"]
        
        x_coords = []
        y_coords = []
        
        for kp in keypoints:
            if kp.confidence > 0.5 and kp.name in major_joints: # Ensure kp.name is not None
                x_coords.append(kp.x)
                y_coords.append(kp.y)
        
        if not x_coords or not y_coords: # If no major joints, try all keypoints
            x_coords = [kp.x for kp in keypoints if kp.confidence > 0.3]
            y_coords = [kp.y for kp in keypoints if kp.confidence > 0.3]
        
        if x_coords and y_coords: # Check if lists are non-empty
            return (np.mean(x_coords), np.mean(y_coords))
        return (0.5, 0.5)  # Default center if no reliable keypoints
    
    def _get_limb_positions(self, keypoints: List[Keypoint]) -> Dict[str, Tuple[float, float]]:
        """Get positions of major limbs. (Currently not heavily used beyond potential debugging)"""
        positions = {}
        for kp in keypoints:
            if kp.confidence > 0.3 and kp.name:
                positions[kp.name] = (kp.x, kp.y)
        return positions
    
    def _compute_direction(self, displacement: Tuple[float, float]) -> Direction:
        """Compute movement direction from displacement vector."""
        dx, dy = displacement
        threshold = 0.005 # Normalized units per frame
        
        if abs(dx) < threshold and abs(dy) < threshold:
            return Direction.STATIONARY
        
        if abs(dx) > abs(dy):
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if dy > 0 else Direction.UP # dy positive is typically down in image coords
    
    def _categorize_speed(self, velocity: float) -> Speed:
        """Categorize velocity into speed levels (velocity is in normalized units/sec)."""
        if velocity < self.velocity_threshold_slow:
            return Speed.SLOW
        elif velocity < self.velocity_threshold_fast:
            return Speed.MODERATE # Corrected from Speed.FAST
        else:
            return Speed.FAST
    
    def _compute_intensity(self, acceleration: float, velocity: float) -> Intensity:
        """Compute movement intensity (accel in norm_units/sec^2, vel in norm_units/sec)."""
        # Thresholds are relative to normalized space and per-second metrics
        if acceleration > self.intensity_accel_threshold * 2 or velocity > self.velocity_threshold_fast:
            return Intensity.HIGH
        elif acceleration > self.intensity_accel_threshold or velocity > self.velocity_threshold_slow:
            return Intensity.MEDIUM
        else:
            return Intensity.LOW
    
    def _compute_fluidity(self, acceleration: float) -> float:
        """
        Compute fluidity score (0-1) based on acceleration (norm_units/sec^2).
        Lower acceleration = higher fluidity.
        """
        max_expected_accel = 0.2 # This is an assumption for normalization, might need tuning.
                                 # Represents a fairly high acceleration in normalized units/sec^2.
        norm_accel = min(abs(acceleration) / max_expected_accel, 1.0) if max_expected_accel > 0 else 0.0
        return 1.0 - norm_accel
    
    def _compute_expansion(self, keypoints: List[Keypoint]) -> float:
        """
        Compute how expanded/contracted the pose is.
        Returns 0-1 where 1 is fully expanded.
        """
        limb_pairs = [
            ("left_wrist", "right_wrist"),
            ("left_ankle", "right_ankle"),
            ("left_wrist", "left_ankle"), 
            ("right_wrist", "right_ankle"),
            # Could add torso diagonals like ("left_shoulder", "right_hip")
        ]
        
        kp_dict = {kp.name: kp for kp in keypoints if kp.confidence > 0.3 and kp.name}
        if not kp_dict: return 0.5 # No reliable keypoints

        distances = []
        for name1, name2 in limb_pairs:
            if name1 in kp_dict and name2 in kp_dict:
                kp1 = kp_dict[name1]
                kp2 = kp_dict[name2]
                # Ensure coordinates are not NaN before calculation
                if not (np.isnan(kp1.x) or np.isnan(kp1.y) or np.isnan(kp2.x) or np.isnan(kp2.y)):
                    dist = np.sqrt((kp1.x - kp2.x)**2 + (kp1.y - kp2.y)**2)
                    distances.append(dist)
        
        if distances:
            avg_dist = np.mean(distances)
            # Max expected distance (e.g., diagonal of normalized 1x1 space is sqrt(2) approx 1.414)
            # This assumes keypoints are normalized.
            max_possible_dist_heuristic = 1.0 # A more conservative heuristic than 1.4, as limbs rarely span the full diagonal.
            return min(avg_dist / max_possible_dist_heuristic, 1.0) if max_possible_dist_heuristic > 0 else 0.0
        
        return 0.5  # Default neutral expansion if no valid pairs
    
    def _smooth_metrics(self, metrics_list: List[MovementMetrics]) -> List[MovementMetrics]:
        """Apply smoothing to reduce noise in metrics using a simple moving average."""
        window_size = 3
        num_metrics = len(metrics_list)

        if num_metrics <= window_size:
            return metrics_list

        smoothed_metrics_list = metrics_list[:] # Work on a copy

        # Fields to smooth
        fields_to_smooth = ["velocity", "acceleration", "fluidity", "expansion"]

        for i in range(num_metrics):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(num_metrics, i + window_size // 2 + 1)
            window = metrics_list[start_idx:end_idx]

            if not window: continue

            for field in fields_to_smooth:
                values = [getattr(m, field) for m in window if hasattr(m, field)]
                if values:
                    setattr(smoothed_metrics_list[i], field, np.mean(values))
        
        return smoothed_metrics_list


def analyze_pose_sequence(pose_sequence: List[List[PoseResult]], 
                         fps: float = 30.0) -> List[MovementMetrics]:
    """
    Convenience function to analyze a pose sequence.
    
    Args:
        pose_sequence: List of pose results per frame
        fps: Video frame rate
        
    Returns:
        List of movement metrics
    """
    analyzer = MovementAnalyzer(fps=fps)
    return analyzer.analyze_movement(pose_sequence)