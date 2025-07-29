"""
Visualizer for creating annotated videos with pose overlays and movement indicators.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
import colorsys
import math
import traceback

from .pose_estimation import PoseResult, Keypoint
from .notation_engine import MovementMetrics, Direction, Intensity, Speed


class PoseVisualizer:
    """Creates visual overlays for pose and movement analysis."""
    
    # COCO skeleton connections for visualization
    COCO_SKELETON = [
        # Face
        (0, 1), (0, 2), (1, 3), (2, 4),  # nose to eyes, eyes to ears
        # Upper body
        (5, 6),  # shoulders
        (5, 7), (7, 9),  # left arm
        (6, 8), (8, 10),  # right arm
        (5, 11), (6, 12),  # shoulders to hips
        # Lower body
        (11, 12),  # hips
        (11, 13), (13, 15),  # left leg
        (12, 14), (14, 16),  # right leg
    ]
    
    # MediaPipe skeleton connections (33 landmarks)
    MEDIAPIPE_SKELETON = [
        # Face connections
        (0, 1), (1, 2), (2, 3), (3, 7),  # left eye region
        (0, 4), (4, 5), (5, 6), (6, 8),  # right eye region
        (9, 10),  # mouth
        # Upper body
        (11, 12),  # shoulders
        (11, 13), (13, 15),  # left arm
        (12, 14), (14, 16),  # right arm
        (11, 23), (12, 24),  # shoulders to hips
        (23, 24),  # hips
        # Lower body
        (23, 25), (25, 27), (27, 29), (27, 31),  # left leg
        (24, 26), (26, 28), (28, 30), (28, 32),  # right leg
        # Hands
        (15, 17), (15, 19), (15, 21),  # left hand
        (16, 18), (16, 20), (16, 22),  # right hand
    ]
    
    def __init__(self, 
                 trail_length: int = 10,
                 show_skeleton: bool = True,
                 show_trails: bool = True,
                 show_direction_arrows: bool = True,
                 show_metrics: bool = True):
        """
        Initialize visualizer.
        
        Args:
            trail_length: Number of previous frames to show in motion trail
            show_skeleton: Whether to draw pose skeleton
            show_trails: Whether to draw motion trails
            show_direction_arrows: Whether to show movement direction arrows
            show_metrics: Whether to display text metrics on frame
        """
        # print("[TRACE] PoseVisualizer.__init__ called")
        self.trail_length = trail_length
        self.show_skeleton = show_skeleton
        self.show_trails = show_trails
        self.show_direction_arrows = show_direction_arrows
        self.show_metrics = show_metrics
        
        # Trail history for each keypoint
        self.trails = {}
        
        # Color mapping for intensity
        self.intensity_colors = {
            Intensity.LOW: (0, 255, 0),      # Green
            Intensity.MEDIUM: (0, 165, 255),  # Orange
            Intensity.HIGH: (0, 0, 255)       # Red
        }
    
    def visualize_frame(self,
                       frame: np.ndarray,
                       pose_results: List[PoseResult],
                       movement_metrics: Optional[MovementMetrics] = None,
                       frame_index: int = 0) -> np.ndarray:
        """
        Add visual annotations to a single frame.
        
        Args:
            frame: Input frame
            pose_results: Pose detection results for this frame
            movement_metrics: Movement analysis metrics for this frame
            frame_index: Current frame index
            
        Returns:
            Annotated frame
        """
        # print(f"[TRACE] visualize_frame(frame_index={frame_index}, num_poses={len(pose_results)})")
        vis_frame = frame.copy()
        if not pose_results:
            # print(f"[DEBUG] Frame {frame_index}: No pose results (no detections)")
            return vis_frame  # No people detected, return original frame
        
        # Draw for each detected person
        for person_idx, pose in enumerate(pose_results):
            if not pose.keypoints or all(math.isnan(kp.x) or math.isnan(kp.y) for kp in pose.keypoints):
                # print(f"[DEBUG] Frame {frame_index}, Person {person_idx}: All keypoints are NaN or missing, skipping drawing for this person.")
                continue
            
            # Update trails
            if self.show_trails:
                self._update_trails(pose, person_idx)
                self._draw_trails(vis_frame, person_idx)
            
            # Draw skeleton
            if self.show_skeleton:
                color = self._get_color_for_metrics(movement_metrics)
                self._draw_skeleton(vis_frame, pose, color)
            
            # Draw keypoints
            self._draw_keypoints(vis_frame, pose, movement_metrics)
            
            # Draw direction arrow
            if self.show_direction_arrows and movement_metrics:
                self._draw_direction_arrow(vis_frame, pose, movement_metrics)
        
        # Draw metrics overlay
        if self.show_metrics and movement_metrics:
            self._draw_metrics_overlay(vis_frame, movement_metrics)
        
        return vis_frame
    
    def generate_overlay_video(self,
                              frames: List[np.ndarray],
                              all_pose_results: List[List[PoseResult]],
                              all_movement_metrics: List[MovementMetrics],
                              output_path: str,
                              fps: float) -> str:
        """
        Generate complete video with overlays.
        
        Args:
            frames: List of video frames
            all_pose_results: Pose results for each frame
            all_movement_metrics: Movement metrics for each frame
            output_path: Path for output video
            fps: Frames per second
            
        Returns:
            Path to created video
        """
        # print(f"[TRACE] generate_overlay_video(num_frames={len(frames)})")
        try:
            if len(frames) != len(all_pose_results) or len(frames) != len(all_movement_metrics):
                raise ValueError("Mismatched lengths between frames, poses, and metrics")
            self.trails = {}
            annotated_frames = []
            for i, (frame, poses, metrics) in enumerate(
                zip(frames, all_pose_results, all_movement_metrics)
            ):
                annotated_frame = self.visualize_frame(frame, poses, metrics, i)
                annotated_frames.append(annotated_frame)
            # print(f"[DEBUG] About to assemble video with {len(annotated_frames)} frames.")
            # for idx, f in enumerate(annotated_frames):
                # print(f"[DEBUG] Frame {idx} shape: {f.shape if hasattr(f, 'shape') else type(f)}")
            from . import video_utils
            return video_utils.assemble_video(annotated_frames, output_path, fps)
        except Exception as e:
            print(f'[FATAL ERROR] Exception during visualization: {e}')
            print(traceback.format_exc())
            raise
    
    def _update_trails(self, pose: PoseResult, person_id: int):
        """Update motion trails for a person."""
        # print(f"[TRACE] _update_trails(person_id={person_id})")
        if person_id not in self.trails:
            self.trails[person_id] = {}
        
        for kp in pose.keypoints:
            if kp.confidence < 0.3:
                continue
                
            if kp.name not in self.trails[person_id]:
                self.trails[person_id][kp.name] = deque(maxlen=self.trail_length)
            
            # Convert normalized coordinates to pixel coordinates
            # This assumes we'll scale them when drawing
            self.trails[person_id][kp.name].append((kp.x, kp.y))
    
    def _draw_trails(self, frame: np.ndarray, person_id: int):
        """Draw motion trails for a person."""
        # print(f"[TRACE] _draw_trails(person_id={person_id})")
        if person_id not in self.trails:
            return
        
        h, w = frame.shape[:2]
        
        for joint_name, trail in self.trails[person_id].items():
            if len(trail) < 2:
                continue
            
            # Draw trail with fading effect
            for i in range(1, len(trail)):
                x1, y1 = trail[i-1]
                x2, y2 = trail[i]
                if math.isnan(x1) or math.isnan(y1) or math.isnan(x2) or math.isnan(y2):
                    # print(f"[DEBUG] _draw_trails: NaN detected in trail for person {person_id}, joint {joint_name}, skipping segment.")
                    continue
                # print(f"[DEBUG] _draw_trails: Converting to int: ({x1}*{w}, {y1}*{h}) and ({x2}*{w}, {y2}*{h})")
                alpha = i / len(trail)
                color = tuple(int(c * alpha) for c in (255, 255, 255))
                
                # Convert normalized to pixel coordinates
                pt1 = (int(x1 * w), int(y1 * h))
                pt2 = (int(x2 * w), int(y2 * h))
                
                # Draw trail segment
                cv2.line(frame, pt1, pt2, color, thickness=max(1, int(3 * alpha)))
    
    def _draw_skeleton(self, frame: np.ndarray, pose: PoseResult, color: Tuple[int, int, int]):
        """Draw pose skeleton."""
        # print(f"[TRACE] _draw_skeleton()")
        h, w = frame.shape[:2]
        
        # Create keypoint lookup
        kp_dict = {kp.name: kp for kp in pose.keypoints if kp.confidence > 0.3}
        
        # Determine which skeleton to use based on available keypoints
        skeleton = self._get_skeleton_for_model(pose.keypoints)
        
        # Map keypoint names to indices
        keypoint_names = self._get_keypoint_names_for_model(pose.keypoints)
        name_to_idx = {name: i for i, name in enumerate(keypoint_names)}
        
        # Draw skeleton connections
        for connection in skeleton:
            idx1, idx2 = connection
            if idx1 < len(keypoint_names) and idx2 < len(keypoint_names):
                name1 = keypoint_names[idx1]
                name2 = keypoint_names[idx2]
                
                if name1 in kp_dict and name2 in kp_dict:
                    kp1 = kp_dict[name1]
                    kp2 = kp_dict[name2]
                    
                    if math.isnan(kp1.x) or math.isnan(kp1.y) or math.isnan(kp2.x) or math.isnan(kp2.y):
                        # print(f"[DEBUG] _draw_skeleton: NaN detected in skeleton for keypoints {name1}, {name2}, skipping line.")
                        continue
                    
                    # print(f"[DEBUG] _draw_skeleton: Converting to int: ({kp1.x}*{w}, {kp1.y}*{h}) and ({kp2.x}*{w}, {kp2.y}*{h})")
                    # Convert to pixel coordinates
                    pt1 = (int(kp1.x * w), int(kp1.y * h))
                    pt2 = (int(kp2.x * w), int(kp2.y * h))
                    
                    # Draw line
                    cv2.line(frame, pt1, pt2, color, thickness=2)
    
    def _draw_keypoints(self, frame: np.ndarray, pose: PoseResult, 
                       metrics: Optional[MovementMetrics] = None):
        """Draw individual keypoints."""
        # print(f"[TRACE] _draw_keypoints()")
        h, w = frame.shape[:2]
        
        for kp in pose.keypoints:
            if kp.confidence < 0.3:
                continue
            
            if math.isnan(kp.x) or math.isnan(kp.y):
                # print(f"[DEBUG] _draw_keypoints: NaN detected in keypoint {kp.name}, skipping.")
                continue
            
            # print(f"[DEBUG] _draw_keypoints: Converting to int: ({kp.x}*{w}, {kp.y}*{h})")
            # Convert to pixel coordinates
            pt = (int(kp.x * w), int(kp.y * h))
            
            # Color based on confidence
            color = self._confidence_to_color(kp.confidence)
            
            # Draw keypoint
            cv2.circle(frame, pt, 4, color, -1)
            cv2.circle(frame, pt, 5, (255, 255, 255), 1)  # White border
    
    def _draw_direction_arrow(self, frame: np.ndarray, pose: PoseResult,
                             metrics: MovementMetrics):
        """Draw arrow indicating movement direction."""
        # print(f"[TRACE] _draw_direction_arrow()")
        if metrics.direction == Direction.STATIONARY:
            return
        
        h, w = frame.shape[:2]
        
        # Get body center
        xs = [kp.x for kp in pose.keypoints if kp.confidence > 0.3 and not math.isnan(kp.x)]
        ys = [kp.y for kp in pose.keypoints if kp.confidence > 0.3 and not math.isnan(kp.y)]
        if not xs or not ys:
            # print(f"[DEBUG] _draw_direction_arrow: No valid keypoints for direction arrow, skipping.")
            return
        # print(f"[DEBUG] _draw_direction_arrow: Converting to int: ({np.mean(xs)}*{w}, {np.mean(ys)}*{h})")
        center_x = np.mean(xs)
        center_y = np.mean(ys)
        if math.isnan(center_x) or math.isnan(center_y):
            # print(f"[DEBUG] _draw_direction_arrow: NaN detected in center, skipping arrow.")
            return
        center = (int(center_x * w), int(center_y * h))
        
        # Calculate arrow endpoint based on direction
        arrow_length = 50
        direction_vectors = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }
        
        if metrics.direction in direction_vectors:
            dx, dy = direction_vectors[metrics.direction]
            end_point = (
                center[0] + int(dx * arrow_length),
                center[1] + int(dy * arrow_length)
            )
            
            # Color based on speed
            color = self._get_color_for_metrics(metrics)
            
            # Draw arrow
            cv2.arrowedLine(frame, center, end_point, color, thickness=3, tipLength=0.3)
    
    def _draw_metrics_overlay(self, frame: np.ndarray, metrics: MovementMetrics):
        """Draw text overlay with movement metrics."""
        # print(f"[TRACE] _draw_metrics_overlay()")
        # Define text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Sanitize metrics
        def safe_metric(val, name):
            if isinstance(val, float) and math.isnan(val):
                # print(f"[DEBUG] _draw_metrics_overlay: {name} is NaN, replacing with 0.0")
                return 0.0
            return val

        velocity = safe_metric(metrics.velocity, "velocity")
        fluidity = safe_metric(metrics.fluidity, "fluidity")
        expansion = safe_metric(metrics.expansion, "expansion")

        lines = [
            f"Direction: {metrics.direction.value}",
            f"Speed: {metrics.speed.value} ({velocity:.2f})",
            f"Intensity: {metrics.intensity.value}",
            f"Fluidity: {fluidity:.2f}",
            f"Expansion: {expansion:.2f}"
        ]
        
        # Draw background rectangle
        y_offset = 30
        max_width = max([cv2.getTextSize(line, font, font_scale, thickness)[0][0] 
                        for line in lines])
        bg_height = len(lines) * 25 + 10
        
        cv2.rectangle(frame, (10, 10), (20 + max_width, 10 + bg_height),
                     (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (20 + max_width, 10 + bg_height),
                     (255, 255, 255), 1)
        
        # Draw text
        for i, line in enumerate(lines):
            color = (255, 255, 255)
            if i == 2:  # Intensity line
                color = self.intensity_colors.get(metrics.intensity, (255, 255, 255))
            
            cv2.putText(frame, line, (15, y_offset + i * 25),
                       font, font_scale, color, thickness)
    
    def _get_color_for_metrics(self, metrics: Optional[MovementMetrics]) -> Tuple[int, int, int]:
        """Get color based on movement metrics."""
        # print(f"[TRACE] _get_color_for_metrics()")
        if metrics is None:
            return (255, 255, 255)  # White default
        
        return self.intensity_colors.get(metrics.intensity, (255, 255, 255))
    
    def _confidence_to_color(self, confidence: float) -> Tuple[int, int, int]:
        """Convert confidence score to color (green=high, red=low)."""
        # print(f"[TRACE] _confidence_to_color(confidence={confidence})")
        # Use HSV color space for smooth gradient
        hue = confidence * 120  # 0=red, 120=green
        rgb = colorsys.hsv_to_rgb(hue / 360, 1.0, 1.0)
        return tuple(int(c * 255) for c in reversed(rgb))  # BGR for OpenCV
    
    def _get_skeleton_for_model(self, keypoints: List[Keypoint]) -> List[Tuple[int, int]]:
        """Determine which skeleton definition to use based on keypoints."""
        # print(f"[TRACE] _get_skeleton_for_model(num_keypoints={len(keypoints)})")
        # Simple heuristic: if we have more than 20 keypoints, use MediaPipe skeleton
        if len(keypoints) > 20:
            return self.MEDIAPIPE_SKELETON
        return self.COCO_SKELETON
    
    def _get_keypoint_names_for_model(self, keypoints: List[Keypoint]) -> List[str]:
        """Get ordered list of keypoint names for the model."""
        # print(f"[TRACE] _get_keypoint_names_for_model(num_keypoints={len(keypoints)})")
        # If keypoints have names, use them
        if keypoints and keypoints[0].name:
            return [kp.name for kp in keypoints]
        
        # Otherwise, use default COCO names
        from .pose_estimation import MoveNetPoseEstimator
        return MoveNetPoseEstimator.KEYPOINT_NAMES


def create_visualization(
    video_path: str,
    pose_results: List[List[PoseResult]],
    movement_metrics: List[MovementMetrics],
    output_path: str,
    show_trails: bool = True,
    show_metrics: bool = True
) -> str:
    """
    Convenience function to create a visualization from a video file.
    
    Args:
        video_path: Path to input video
        pose_results: Pose detection results
        movement_metrics: Movement analysis results
        output_path: Path for output video
        show_trails: Whether to show motion trails
        show_metrics: Whether to show metrics overlay
        
    Returns:
        Path to created video
    """
    from . import video_utils
    
    # Extract frames
    frames = list(video_utils.extract_frames(video_path))
    
    # Get video info
    _, fps, _ = video_utils.get_video_info(video_path)
    
    # Create visualizer
    visualizer = PoseVisualizer(
        show_trails=show_trails,
        show_metrics=show_metrics
    )
    
    # Generate overlay video
    return visualizer.generate_overlay_video(
        frames, pose_results, movement_metrics, output_path, fps
    ) 