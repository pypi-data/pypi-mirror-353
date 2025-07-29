
import numpy as np
import gi

from video_fragment_ingest._generated.models.graph_models_pb2 import Camera

gi.require_version('Gst', '1.0')
from gi.repository import Gst


class DecodedFrame:
    """
    Represents a single decoded video frame, including metadata and raw pixel data.

    Attributes:
        camera (Camera): Metadata about the camera that produced the frame.
        timestamp (int): Presentation timestamp (PTS) of the frame in seconds.
        frame_caps (Gst.Caps): GStreamer capabilities associated with the frame (e.g. resolution, format).
        frame_number (int): Sequential number of the frame in the stream.
        np_frame (np.ndarray): The actual decoded frame data as a NumPy array as RGB.
    """

    def __init__(
            self,
            camera: Camera,
            timestamp: int,
            frame_caps: Gst.Caps,
            frame_number: int,
            np_frame: np.ndarray
    ):
        self.camera = camera
        self.timestamp = timestamp
        self.frame_caps = frame_caps
        self.frame_number = frame_number
        self.np_frame = np_frame
