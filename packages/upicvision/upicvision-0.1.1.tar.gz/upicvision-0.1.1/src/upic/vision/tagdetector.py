"""
AprilTag Detection Module

This module provides comprehensive AprilTag detection capabilities using computer vision
techniques. It supports real-time camera-based tag detection with configurable processing
options and multi-threading support for optimal performance.

Features:
    - Real-time AprilTag detection from camera feeds
    - Configurable tag selection methods (nearest, single)
    - Thread-safe detection with start/stop/pause controls
    - Automatic camera buffer management for low-latency processing
    - Comprehensive logging and error handling
    - Performance testing utilities

Example:
    Basic usage for AprilTag detection:
    
    >>> detector = TagDetector(cam_id=0, resolution_multiplier=0.5)
    >>> detector.open_camera().apriltag_detect_start()
    >>> current_tag_id = detector.tag_id
    >>> detector.apriltag_detect_end().release_camera()
"""

from dataclasses import dataclass
from threading import Thread
from time import sleep
from typing import List, Literal, Self, Any, Callable, Optional

import cv2
import numpy as np
from cv2 import Mat, cvtColor, COLOR_RGB2GRAY, VideoCapture
from numpy import ndarray, dtype, generic
from numpy.linalg import linalg
from pyapriltags import Detector, Detection

from ..modules.logger import _logger


class TagDetector:
    """
    A comprehensive AprilTag detection system for real-time computer vision applications.
    
    This class provides a complete solution for detecting AprilTags from camera feeds with
    configurable detection strategies, automatic resource management, and thread-safe operation.
    It supports both single-tag and multi-tag detection scenarios with various selection methods.
    
    The detector operates in a separate thread to ensure non-blocking operation and includes
    built-in camera buffer management for optimal real-time performance.
    
    Attributes:
        detector (Detector): Static AprilTag detector instance configured for tag36h11 family
        
    Example:
        >>> # Initialize detector with camera 0 and half resolution
        >>> detector = TagDetector(cam_id=0, resolution_multiplier=0.5)
        >>> 
        >>> # Start detection process
        >>> detector.apriltag_detect_start()
        >>> 
        >>> # Access detected tag ID
        >>> tag_id = detector.tag_id
        >>> 
        >>> # Clean up resources
        >>> detector.apriltag_detect_end().release_camera()
    
    Note:
        The detector uses the tag36h11 family by default, which provides a good balance
        between detection reliability and computational efficiency.
    """

    detector = Detector(
        families="tag36h11",
        nthreads=2,
        quad_decimate=1.0,
        refine_edges=False,
        debug=False,
    )

    @dataclass
    class Config:
        """
        Configuration parameters for TagDetector behavior.
        
        This dataclass contains all configurable parameters that control the detection
        process, camera settings, and operational behavior of the TagDetector.
        
        Attributes:
            single_tag_mode (bool): Whether to operate in single tag detection mode.
                Defaults to True for most use cases.
            resolution_multiplier (float): Multiplier for camera resolution scaling.
                Values < 1.0 reduce resolution for better performance. Defaults to 0.5.
            ordering_method (Literal["nearest", "single"]): Method for selecting tags
                when multiple are detected. "nearest" selects closest to frame center,
                "single" selects the first detected tag. Defaults to "nearest".
            halt_check_interval (float): Time interval in seconds between halt status
                checks during detection loop. Defaults to 0.4 seconds.
            default_tag_id (int): Tag ID returned when no tags are detected.
                Defaults to -1.
            error_tag_id (int): Tag ID returned when camera errors occur.
                Defaults to -10.
            buffer_size (int): Camera buffer size for real-time performance.
                Smaller values reduce latency. Defaults to 2.
        """
        single_tag_mode: bool = True
        resolution_multiplier: float = 0.5
        ordering_method: Literal["nearest", "single"] = "nearest"
        halt_check_interval: float = 0.4
        default_tag_id: int = -1
        error_tag_id: int = -10
        buffer_size: int = 2

    def __init__(
        self,
        cam_id: Optional[int] = None,
        resolution_multiplier: Optional[float] = None,
    ):
        """
        Initialize the TagDetector with optional camera and resolution settings.
        
        Creates a new TagDetector instance with the specified camera device and resolution
        settings. If a camera ID is provided, the camera will be automatically opened and
        configured. The detector starts in an idle state and requires explicit activation
        via apriltag_detect_start().
        
        Args:
            cam_id (Optional[int]): Camera device ID to open automatically. If None,
                camera must be opened manually using open_camera(). Defaults to None.
            resolution_multiplier (Optional[float]): Multiplier for camera resolution
                scaling. If None, uses Config.resolution_multiplier. Values less than
                1.0 reduce resolution for better performance. Defaults to None.
                
        Raises:
            ValueError: If camera initialization fails or resolution setting is invalid.
            
        Example:
            >>> # Initialize without camera (manual setup required)
            >>> detector = TagDetector()
            >>> 
            >>> # Initialize with camera 0 and custom resolution
            >>> detector = TagDetector(cam_id=0, resolution_multiplier=0.75)
            
        Note:
            Camera buffer configuration is automatically applied when a camera is opened
            to ensure optimal real-time performance with minimal latency.
        """
        self._frame_center: ndarray = np.array([0, 0])
        self._camera: VideoCapture | None = None
        if cam_id is not None:
            self._camera = VideoCapture(cam_id)
            self._configure_camera_buffer()
        self.set_cam_resolution_mul(
            resolution_multiplier or self.Config.resolution_multiplier
        ) if self._camera else None

        self._tag_id: int = TagDetector.Config.default_tag_id

        self._continue_detection: bool = False
        self._halt_detection: bool = False

    def _configure_camera_buffer(self) -> None:
        """
        Configure camera buffer size for optimal real-time performance.
        
        This internal method sets the camera's frame buffer size to the configured value
        to minimize latency in real-time applications. A smaller buffer size ensures that
        frames are processed with minimal delay, which is crucial for responsive tag detection.
        
        The method only operates when a camera instance is available and logs the
        configuration for debugging purposes.
        
        Note:
            This is an internal method and should not be called directly by users.
            It is automatically invoked during camera initialization and opening.
            
        Side Effects:
            - Modifies camera buffer size property
            - Logs buffer configuration information
        """
        if self._camera is not None:
            # Set buffer size to configured value to ensure we get frames with desired buffering
            self._camera.set(cv2.CAP_PROP_BUFFERSIZE, self.Config.buffer_size)
            _logger.info(f"Camera buffer size set to {self.Config.buffer_size} for real-time performance")

    def open_camera(self, device_id: int = 0) -> Self:
        """
        Open and configure a camera device for AprilTag detection.
        
        This method initializes a camera connection, configures it for optimal performance,
        and prepares it for tag detection. If a camera is already open, it will be properly
        released before opening the new one. The method includes comprehensive error checking
        and logging of camera properties.
        
        Args:
            device_id (int): Camera device identifier. Typically 0 for the default camera,
                1 for the second camera, etc. Defaults to 0.
                
        Returns:
            Self: The TagDetector instance for method chaining.
            
        Raises:
            RuntimeError: If the camera cannot be opened or configured properly.
            
        Example:
            >>> detector = TagDetector()
            >>> detector.open_camera(0)  # Open default camera
            >>> detector.open_camera(1)  # Switch to second camera
            
        Note:
            The method automatically configures camera buffer size, updates frame center
            calculations, and logs detailed camera information including resolution,
            frame rate, and buffer settings for debugging purposes.
            
        Side Effects:
            - Releases any existing camera connection
            - Opens new camera connection
            - Configures camera buffer for real-time performance
            - Updates internal frame center calculations
            - Logs comprehensive camera configuration information
        """
        if self._camera is not None:
            self.release_camera()
        self._camera = cv2.VideoCapture(device_id)
        if self._camera.isOpened():
            self._configure_camera_buffer()
            self._update_cam_center()
            _logger.info(
                f"CAMERA RESOLUTION：{self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}\n"
                f"CAMERA FPS: [{self._camera.get(cv2.CAP_PROP_FPS)}]\n"
                f"CAM CENTER: [{self._frame_center}]\n"
                f"BUFFER SIZE: [{self._camera.get(cv2.CAP_PROP_BUFFERSIZE)}]"
            )
        else:
            _logger.error("Can't open camera!")
        return self

    def release_camera(self) -> Self:
        """
        Release the camera resource and clean up associated connections.

        This method properly releases the camera resource to free system resources and
        ensure the camera is available for other applications. It includes comprehensive
        error checking and logging to track resource management.

        Returns:
            Self: The TagDetector instance for method chaining, supporting fluent interface.
            
        Example:
            >>> detector = TagDetector()
            >>> detector.open_camera(0).apriltag_detect_start()
            >>> # ... perform detection ...
            >>> detector.apriltag_detect_end().release_camera()
            
        Note:
            It's important to call this method when finished with the camera to prevent
            resource leaks and ensure proper cleanup. The method is safe to call multiple
            times and will only log a warning if no camera is currently allocated.
            
        Side Effects:
            - Releases OpenCV VideoCapture resource
            - Sets internal camera reference to None
            - Logs resource management operations
        """
        if self._camera:
            _logger.info("Releasing camera...")
            self._camera.release()  # Release the camera resource
            self._camera = None
            _logger.info("Camera released!")
        else:
            _logger.warning("There is no camera need to release!")
        return self  # Support chaining calls

    def apriltag_detect_start(self) -> Self:
        """
        Start the AprilTag detection process in a separate thread.

        This method initializes and starts the continuous AprilTag detection process in
        a dedicated daemon thread. The detection loop processes camera frames in real-time,
        applying the configured tag selection method and updating the internal tag ID.
        
        The detection process supports two ordering methods:
        - "nearest": Selects the tag closest to the frame center
        - "single": Selects the first detected tag in the list
        
        Returns:
            Self: The TagDetector instance for method chaining.
            
        Raises:
            ValueError: If camera is not initialized or configuration method is invalid.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.apriltag_detect_start()
            >>> # Detection runs in background thread
            >>> tag_id = detector.tag_id  # Access current detection result
            >>> detector.apriltag_detect_end()  # Stop detection when done
            
        Note:
            The detection thread is marked as daemon, so it will automatically terminate
            when the main program exits. The thread includes comprehensive error handling
            and will log exceptions while attempting to continue operation.
            
        Thread Safety:
            This method is thread-safe and the detection loop properly handles concurrent
            access to shared state variables through atomic operations.
            
        Side Effects:
            - Creates and starts a new daemon thread for detection
            - Sets detection flags to active state
            - Begins continuous camera frame processing
            - Updates internal tag ID based on detection results
        """

        if self._camera is None:
            raise ValueError("Camera is not initialized! Use open_camera() first!")

        # Set the tag detection function
        detector_function = TagDetector.detector.detect

        # Retrieve the camera instance and frame center
        cam = self._camera
        frame_center: ndarray = self._frame_center
        check_interval = self.Config.halt_check_interval

        _logger.info(f"Tag detecting mode: {self.Config.ordering_method}")
        # Choose the tag handling method based on the configuration
        match self.Config.ordering_method:
            case "nearest":
                # Select the nearest tag handling method
                used_method: Callable[[List[Detection]], int] = lambda tags: min(
                    tags, key=lambda tag: linalg.norm(tag.center - frame_center)
                ).tag_id
            case "single":
                # Select the method to handle the first detected tag
                used_method: Callable[[List[Detection]], int] = lambda tags: tags[
                    0
                ].tag_id
            case _:
                # Raise an error if the configuration method is invalid
                raise ValueError(
                    f"Wrong ordering method! Got {self.Config.ordering_method}"
                )

        default_tag_id = TagDetector.Config.default_tag_id
        error_tag_id = TagDetector.Config.error_tag_id

        def __loop():
            try:
                # Main detection loop
                while self._continue_detection:
                    # Check if detection should be halted
                    if self._halt_detection:
                        _logger.debug("Apriltag detect halted!")
                        sleep(check_interval)
                        continue
                    # Read a frame from the camera
                    success, frame = cam.read()
                    if success:
                        # Convert the frame to grayscale and detect tags
                        gray: Mat | ndarray[Any, dtype[generic]] | ndarray = cvtColor(
                            frame, COLOR_RGB2GRAY
                        )
                        tags: List[Detection] = detector_function(gray)
                        if tags:
                            # Update the tag ID using the selected method
                            self._tag_id = used_method(tags)
                        else:
                            # If no tags are detected, set the tag ID to the error tag ID
                            self._tag_id = default_tag_id
                    else:
                        # If the camera read fails, log a critical error and set the error tag ID
                        self._tag_id = error_tag_id
                        _logger.critical("Camera not functional!")
                        break
            except Exception as e:
                _logger.exception(e)
            # Log when the detection loop stops
            _logger.info("AprilTag detect stopped")

        self._continue_detection = True
        # Create and start the detection thread
        apriltag_detect = Thread(
            target=__loop, name="apriltag_detect_Process", daemon=True
        )
        apriltag_detect.start()
        # Log when the detection is activated
        _logger.info("AprilTag detect Activated")
        return self

    def apriltag_detect_end(self) -> Self:
        """
        Stop the AprilTag detection process and reset the tag ID.

        This method gracefully terminates the detection thread by setting the control
        flags and resets the internal tag ID to the default value. The detection thread
        will complete its current iteration and then exit cleanly.

        Returns:
            Self: The TagDetector instance for method chaining.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.apriltag_detect_start()
            >>> # ... perform detection operations ...
            >>> detector.apriltag_detect_end()  # Stop detection
            
        Note:
            This method only signals the detection thread to stop; it does not forcibly
            terminate the thread. The thread will stop after completing its current
            processing cycle, ensuring clean shutdown without resource corruption.
            
        Side Effects:
            - Sets detection continuation flag to False
            - Resets internal tag ID to default value
            - Allows detection thread to terminate gracefully
        """
        self._continue_detection = False
        self._tag_id = TagDetector.Config.default_tag_id
        return self

    def halt_detection(self) -> Self:
        """
        Temporarily halt the tag detection process without stopping the thread.

        This method pauses the detection process while keeping the detection thread active.
        The thread will enter a sleep state and periodically check for resume signals.
        The tag ID is reset to the default value during the halt period.

        Returns:
            Self: The TagDetector instance for method chaining.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.apriltag_detect_start()
            >>> detector.halt_detection()    # Pause detection
            >>> detector.resume_detection()  # Resume detection
            
        Note:
            Unlike apriltag_detect_end(), this method keeps the detection thread alive
            but inactive, allowing for quick resumption without thread recreation overhead.
            The thread will sleep for Config.halt_check_interval between status checks.
            
        Side Effects:
            - Sets halt detection flag to True
            - Resets internal tag ID to default value
            - Detection thread enters periodic sleep state
        """
        self._halt_detection = True
        self._tag_id = TagDetector.Config.default_tag_id
        return self

    def resume_detection(self) -> Self:
        """
        Resume the halted tag detection process.

        This method resumes detection that was previously halted using halt_detection().
        The detection thread will immediately exit its sleep state and begin processing
        camera frames again in the next iteration.

        Returns:
            Self: The TagDetector instance for method chaining.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.apriltag_detect_start()
            >>> detector.halt_detection()    # Pause detection
            >>> # ... do other work ...
            >>> detector.resume_detection()  # Resume detection immediately
            
        Note:
            This method only works if the detection thread is currently active but halted.
            If the detection thread has been stopped with apriltag_detect_end(), you must
            call apriltag_detect_start() instead to restart the detection process.
            
        Side Effects:
            - Sets halt detection flag to False
            - Detection thread resumes frame processing on next iteration
        """
        self._halt_detection = False
        return self

    @property
    def tag_id(self) -> int:
        """
        Get the currently detected AprilTag ID.
        
        This property provides thread-safe access to the most recently detected tag ID.
        The value is updated continuously by the detection thread when active.
        
        Returns:
            int: The ID of the currently detected AprilTag. Returns Config.default_tag_id
                when no tags are detected, Config.error_tag_id when camera errors occur,
                or the actual tag ID when a tag is successfully detected.
                
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.apriltag_detect_start()
            >>> current_tag = detector.tag_id
            >>> if current_tag >= 0:
            >>>     print(f"Detected tag: {current_tag}")
            >>> elif current_tag == TagDetector.Config.default_tag_id:
            >>>     print("No tag detected")
            >>> elif current_tag == TagDetector.Config.error_tag_id:
            >>>     print("Camera error")
                
        Note:
            The tag ID is updated atomically by the detection thread, so this property
            is safe to access from multiple threads without additional synchronization.
        """
        return self._tag_id

    def _update_cam_center(self) -> None:
        """
        Update the internal frame center coordinates based on current camera resolution.
        
        This internal method recalculates the center point of the camera frame based on
        the current camera resolution settings. It's used internally for "nearest" tag
        selection mode to determine which detected tag is closest to the frame center.
        
        Note:
            This is an internal method and should not be called directly by users.
            It is automatically invoked when camera resolution changes or camera
            is opened/configured.
            
        Side Effects:
            - Updates internal _frame_center numpy array with current resolution center
        """
        self._frame_center = np.array(
            [
                self._camera.get(cv2.CAP_PROP_FRAME_WIDTH) / 2,
                self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2,
            ]
        )

    def set_cam_resolution_mul(
        self,
        resolution_multiplier: float,
    ) -> Self:
        """
        Set camera resolution by multiplying current resolution with a scaling factor.

        This method provides a convenient way to scale the camera resolution while
        maintaining the aspect ratio. It's particularly useful for balancing detection
        performance with processing speed.

        Args:
            resolution_multiplier (float): Scaling factor for resolution adjustment.
                Values > 1.0 increase resolution (better quality, slower processing),
                values < 1.0 decrease resolution (faster processing, lower quality).
                For example, 0.5 reduces resolution to half in both dimensions.

        Returns:
            Self: The TagDetector instance for method chaining.
            
        Raises:
            ValueError: If camera is not initialized.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.set_cam_resolution_mul(0.5)   # Half resolution for speed
            >>> detector.set_cam_resolution_mul(1.5)   # 1.5x resolution for quality
            
        Note:
            The actual resolution set may be adjusted by the camera driver to the
            nearest supported resolution. The method automatically updates the frame
            center calculations after resolution changes.
            
        Side Effects:
            - Modifies camera resolution properties
            - Updates internal frame center calculations
            - Logs new resolution settings
        """
        if self._camera is None:
            raise ValueError("Camera is not initialized!")
        return self.set_cam_resolution(
            self._camera.get(cv2.CAP_PROP_FRAME_WIDTH) * resolution_multiplier,
            self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT) * resolution_multiplier,
        )

    def set_cam_resolution(
        self, new_width: int | float, new_height: int | float
    ) -> Self:
        """
        Set the camera resolution to specific width and height values.

        This method directly sets the camera resolution to the specified dimensions.
        The camera driver may adjust the values to the nearest supported resolution.

        Args:
            new_width (int | float): Target width in pixels. Non-integer values
                will be converted to integers by the camera driver.
            new_height (int | float): Target height in pixels. Non-integer values
                will be converted to integers by the camera driver.

        Returns:
            Self: The TagDetector instance for method chaining.
            
        Raises:
            ValueError: If camera is not initialized.
            
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> detector.set_cam_resolution(640, 480)    # VGA resolution
            >>> detector.set_cam_resolution(1920, 1080)  # Full HD resolution
            
        Note:
            Common resolutions include:
            - 640x480 (VGA): Good balance of speed and quality
            - 1280x720 (HD): Higher quality, moderate processing load
            - 1920x1080 (Full HD): Highest quality, highest processing load
            
            The method automatically updates frame center calculations and logs
            the actual resolution set by the camera driver.
            
        Side Effects:
            - Modifies camera width and height properties
            - Updates internal frame center calculations
            - Logs actual resolution achieved by camera driver
        """
        if self._camera is None:
            raise ValueError("Camera is not initialized!")
        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, new_width)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, new_height)
        _logger.info(
            f"Set CAMERA RESOLUTION: {self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}"
        )
        self._update_cam_center()
        return self

    @property
    def camera_device(self) -> cv2.VideoCapture | None:
        """
        Get the underlying OpenCV VideoCapture device instance.
        
        This property provides direct access to the OpenCV VideoCapture object for
        advanced camera operations not covered by the TagDetector interface. Use
        with caution as direct manipulation may interfere with detection operations.
        
        Returns:
            cv2.VideoCapture | None: The VideoCapture instance if a camera is open,
                None if no camera is currently initialized.
                
        Example:
            >>> detector = TagDetector(cam_id=0)
            >>> camera = detector.camera_device
            >>> if camera is not None:
            >>>     # Direct OpenCV operations
            >>>     ret, frame = camera.read()
            >>>     fps = camera.get(cv2.CAP_PROP_FPS)
                
        Warning:
            Direct manipulation of the camera device may interfere with the detection
            process. It's recommended to halt detection before performing direct
            camera operations and resume afterward.
            
        Note:
            This property is primarily intended for advanced users who need access
            to camera features not exposed through the TagDetector interface.
        """
        return self._camera


def test_frame_time(camera: cv2.VideoCapture, test_frames_count: int = 600) -> float:
    """
    Benchmark camera frame acquisition performance over multiple samples.
    
    This utility function measures the time required to read frames from a camera
    over a specified number of iterations and provides statistical analysis of
    the timing performance. It's useful for optimizing camera settings and
    evaluating system performance for real-time applications.
    
    Args:
        camera (cv2.VideoCapture): OpenCV VideoCapture instance to test. The camera
            should already be opened and configured before calling this function.
        test_frames_count (int): Number of frame read operations to perform for
            the benchmark. Higher values provide more accurate statistics but
            take longer to complete. Defaults to 600 frames.
            
    Returns:
        float: Average frame acquisition time in seconds per frame. This represents
            the mean time required for a single camera.read() operation.
            
    Example:
        >>> import cv2
        >>> camera = cv2.VideoCapture(0)
        >>> avg_time = test_frame_time(camera, 1000)
        >>> max_fps = 1.0 / avg_time
        >>> print(f"Average frame time: {avg_time:.4f}s, Max FPS: {max_fps:.1f}")
        >>> camera.release()
        
    Note:
        This function performs blocking frame reads and will take significant time
        to complete based on the test_frames_count parameter. For 600 frames at
        30 FPS, expect the test to take approximately 20 seconds.
        
        The function prints detailed statistics including total time, average frame
        time, and standard deviation to help identify performance characteristics
        and potential timing inconsistencies.
        
    Performance Considerations:
        - Higher frame counts provide more accurate statistics
        - Results may vary based on camera resolution and system load
        - USB cameras typically have higher latency than built-in cameras
        - Buffer size settings can significantly impact timing consistency
    """
    from timeit import repeat
    from numpy import mean, std

    durations: List[float] = repeat(
        stmt=camera.read, number=1, repeat=test_frames_count
    )
    hall_duration: float = sum(durations)
    average_duration: float = float(mean(hall_duration))
    std_error = std(a=durations, ddof=1)
    print(
        "Frame Time Test Results: \n"
        f"\tRunning on [{test_frames_count}] frame updates\n"
        f"\tTotal Time Cost: [{hall_duration}]\n"
        f"\tAverage Frame time: [{average_duration}]\n"
        f"\tStd Error: [{std_error}]\n"
    )
    return average_duration
