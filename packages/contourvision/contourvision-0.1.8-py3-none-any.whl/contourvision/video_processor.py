import cv2
import numpy as np
import os

class VideoContourExtractor:
    """
    A class for extracting contours from video frames using different methods.
    """
    def __init__(self, 
                 contour_style='white_on_black',
                 threshold_type='otsu', 
                 threshold_value=127,
                 adaptive_block_size=11,
                 adaptive_c=2,
                 # Parameters for 'opencv_level_contours' style
                 num_levels=5, 
                 explicit_levels=None,
                 level_contour_color=(0, 0, 0), # Black contours
                 level_background_color=(255, 255, 255), # White background
                 invert_level_output=False 
                ):
        """
        Initializes the VideoContourExtractor.

        Args:
            contour_style (str): The style of the output contours.
                                 'white_on_black' - OpenCV contours on black background.
                                 'black_on_white' - OpenCV contours on white background.
                                 'opencv_level_contours' - Contours at multiple intensity levels.
            threshold_type (str): The thresholding method for styles that create a binary image
                                  (e.g., 'white_on_black', 'black_on_white').
                                  Supported: 'otsu', 'fixed', 'adaptive_mean', 
                                             'adaptive_gaussian', 'triangle'.
            threshold_value (int): The threshold value (0-255) for 'fixed' threshold_type.
            adaptive_block_size (int): Size of the pixel neighborhood for adaptive thresholding.
                                       Must be odd and > 1.
            adaptive_c (int): Constant subtracted from the mean or weighted mean for adaptive
                              thresholding. Can be positive, zero, or negative.
            
            For 'opencv_level_contours' style:
            num_levels (int): Number of intensity levels to find contours at if explicit_levels is None.
            explicit_levels (list of int, optional): Specific intensity levels (0-255) to find contours at.
            level_contour_color (tuple BGR): Color of the contour lines for 'opencv_level_contours'.
            level_background_color (tuple BGR): Background color for 'opencv_level_contours'.
            invert_level_output (bool): If True, inverts the final output colors for 'opencv_level_contours'.
        """
        self.contour_style = contour_style.lower()
        self.threshold_type = threshold_type.lower()
        self.threshold_value = threshold_value
        self.adaptive_block_size = adaptive_block_size
        self.adaptive_c = adaptive_c

        # Store parameters for 'opencv_level_contours'
        self.num_levels = num_levels
        self.explicit_levels = explicit_levels
        self.level_contour_color = level_contour_color
        self.level_background_color = level_background_color
        self.invert_level_output = invert_level_output

        # Supported styles
        self.supported_binary_styles = ['white_on_black', 'black_on_white']
        self.supported_level_styles = ['opencv_level_contours']
        self.all_styles = self.supported_binary_styles + self.supported_level_styles

        if self.contour_style not in self.all_styles:
            raise ValueError(f"Unsupported 'contour_style'. Supported values: {', '.join(self.all_styles)}.")

        # Supported threshold types for binary styles
        self.supported_threshold_types = ['otsu', 'fixed', 'adaptive_mean', 'adaptive_gaussian', 'triangle']
        
        if self.contour_style in self.supported_binary_styles:
            if self.threshold_type not in self.supported_threshold_types:
                raise ValueError(
                    f"Unsupported 'threshold_type' for '{self.contour_style}'. "
                    f"Supported values: {', '.join(self.supported_threshold_types)}."
                )
            if self.threshold_type == 'fixed':
                if not (0 <= self.threshold_value <= 255):
                    raise ValueError("'threshold_value' must be between 0 and 255 for 'fixed' thresholding.")
            if self.threshold_type in ['adaptive_mean', 'adaptive_gaussian']:
                if not isinstance(self.adaptive_block_size, int) or self.adaptive_block_size <= 1 or self.adaptive_block_size % 2 == 0:
                    raise ValueError("'adaptive_block_size' must be an odd integer greater than 1.")
                if not isinstance(self.adaptive_c, (int, float)):
                     raise ValueError("'adaptive_c' must be a number.")
        
        if self.contour_style in self.supported_level_styles:
            if not isinstance(self.num_levels, int) or self.num_levels < 1:
                raise ValueError("'num_levels' must be a positive integer.")
            if self.explicit_levels is not None:
                if not isinstance(self.explicit_levels, list) or not all(isinstance(lvl, int) and 0 <= lvl <= 255 for lvl in self.explicit_levels):
                    raise ValueError("'explicit_levels' must be a list of integers between 0 and 255.")
        
        print(f"VideoContourExtractor initialized: style='{self.contour_style}'")
        if self.contour_style in self.supported_binary_styles:
            print(f"  Thresholding method='{self.threshold_type}'")
            if self.threshold_type == 'fixed':
                print(f"    Threshold value='{self.threshold_value}'")
            elif self.threshold_type in ['adaptive_mean', 'adaptive_gaussian']:
                print(f"    Adaptive block size='{self.adaptive_block_size}'")
                print(f"    Adaptive C='{self.adaptive_c}'")
        elif self.contour_style in self.supported_level_styles:
            print(f"  Number of levels='{self.num_levels if self.explicit_levels is None else len(self.explicit_levels)}'")
            print(f"  Contour color='{self.level_contour_color}', Background='{self.level_background_color}'")


    def process_video(self, input_video_path: str, output_video_path: str):
        """
        Reads a video, finds contours in each frame according to the settings,
        and writes the result to a new video file.
        """
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Error: Input video file not found at: {input_video_path}")
        
        cap = None
        out = None
        try:
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                print(f"Error: Could not open video file: {input_video_path}")
                return

            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Output is color only if 'opencv_level_contours' style is used.
            # Otherwise, it's a binary (grayscale) image.
            is_color_output = self.contour_style == 'opencv_level_contours'
            
            output_dir = os.path.dirname(output_video_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")

            # Using 'XVID' for .avi as it's widely compatible.
            # For .mp4, 'mp4v' or 'H264' might be better but can be system-dependent.
            fourcc = cv2.VideoWriter_fourcc(*'XVID') 
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=is_color_output)
            if not out.isOpened():
                print(f"Error: Could not open VideoWriter for output file: {output_video_path}")
                print("Please check codec availability and write permissions.")
                if cap is not None and cap.isOpened(): cap.release()
                return


            print(f"Starting video processing: '{input_video_path}' -> '{output_video_path}' (Style: {self.contour_style}, Threshold: {self.threshold_type if self.contour_style in self.supported_binary_styles else 'N/A'})")
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Total frames to process: {total_frames if total_frames > 0 else 'N/A'}")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break 

                processed_frame = self._process_frame(frame, frame_width, frame_height)
                
                # Ensure frame is in the correct format for writing (e.g. BGR for color, grayscale for mono)
                if is_color_output and len(processed_frame.shape) == 2: # Grayscale frame but color output expected
                    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
                elif not is_color_output and len(processed_frame.shape) == 3: # Color frame but grayscale output expected
                     print(f"Warning: Processed frame for style {self.contour_style} is color, but output is grayscale. Converting.")
                     processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)


                out.write(processed_frame)
                frame_count += 1
                if total_frames > 0 and frame_count % 100 == 0 : 
                    progress = (frame_count / total_frames) * 100
                    print(f"Processed frames: {frame_count}/{total_frames} ({progress:.2f}%)")
                elif frame_count % 100 == 0:
                    print(f"Processed frames: {frame_count}")

            print(f"Video processing finished. Processed {frame_count} frames. Result saved to: {output_video_path}")

        except Exception as e:
            print(f"An error occurred during video processing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if cap is not None and cap.isOpened():
                cap.release()
            if out is not None:
                out.release()

    def _process_frame(self, frame: np.ndarray, frame_width: int, frame_height: int) -> np.ndarray:
        """
        Processes a single video frame.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.contour_style == 'opencv_level_contours':
            # Determine levels for contouring
            if self.explicit_levels:
                levels_to_process = sorted(list(set(self.explicit_levels))) # Use unique sorted levels
            else:
                min_val, max_val, _, _ = cv2.minMaxLoc(gray_frame)
                if max_val == min_val: # Avoid division by zero if frame is flat
                    levels_to_process = [int(min_val)] if self.num_levels >=1 else []
                else:
                    # Exclude absolute min/max for potentially cleaner visuals unless only 1 level is requested
                    if self.num_levels == 1:
                         levels_to_process = [int((min_val + max_val) / 2)]
                    else:
                        levels_to_process = np.linspace(min_val, max_val, self.num_levels + 2, dtype=int)[1:-1] 
                    
                    if not levels_to_process.any() and self.num_levels >=1: 
                        levels_to_process = [int((min_val + max_val) / 2)]


            # Create a BGR canvas for drawing colored contours
            output_canvas = np.full((frame_height, frame_width, 3), self.level_background_color, dtype=np.uint8)

            for level in levels_to_process:
                _, binary_at_level = cv2.threshold(gray_frame, int(level), 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(binary_at_level, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(output_canvas, contours, -1, self.level_contour_color, 1) 

            if self.invert_level_output:
                output_canvas = cv2.bitwise_not(output_canvas) # More reliable than 255 - canvas for color
            
            return output_canvas

        elif self.contour_style in self.supported_binary_styles:
            binary_image = None
            # Determine OpenCV threshold flags based on contour style
            # For 'white_on_black': objects should be white (255), background black (0) after thresholding.
            # For 'black_on_white': objects should be black (0), background white (255) after thresholding.
            # Contours are typically found on white objects against a black background.

            if self.threshold_type == 'otsu':
                # white_on_black: THRESH_BINARY (object becomes white if > thresh) + THRESH_OTSU
                # black_on_white: THRESH_BINARY_INV (object becomes white if < thresh) + THRESH_OTSU, then invert image or draw black contours on white.
                # Simpler: always get white objects on black background for contour finding, then adjust canvas.
                _, binary_image_for_contours = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            elif self.threshold_type == 'triangle':
                _, binary_image_for_contours = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)

            elif self.threshold_type == 'fixed':
                # Get white objects on black background
                _, binary_image_for_contours = cv2.threshold(gray_frame, self.threshold_value, 255, cv2.THRESH_BINARY)

            elif self.threshold_type == 'adaptive_mean':
                # For adaptive thresholding, THRESH_BINARY means if pixel > threshold it's set to maxval.
                # We want white objects on black for findContours.
                # cv2.ADAPTIVE_THRESH_MEAN_C: threshold = mean(neighborhood) - C
                # If pixel > mean-C, it becomes 255. This makes brighter regions white.
                binary_image_for_contours = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                   cv2.THRESH_BINARY, self.adaptive_block_size, self.adaptive_c)
            
            elif self.threshold_type == 'adaptive_gaussian':
                binary_image_for_contours = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                   cv2.THRESH_BINARY, self.adaptive_block_size, self.adaptive_c)
            else:
                # Fallback, should have been caught by __init__
                print(f"Warning: Unsupported threshold type '{self.threshold_type}'. Defaulting to OTSU.")
                _, binary_image_for_contours = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Find contours on the (white object, black background) binary image
            contours, _ = cv2.findContours(binary_image_for_contours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Prepare output frame based on contour_style
            if self.contour_style == 'white_on_black':
                # White contours on black background
                output_contour_frame = np.zeros((frame_height, frame_width), dtype=np.uint8)
                cv2.drawContours(output_contour_frame, contours, -1, (255), 1) # Draw white contours
            else: # black_on_white
                # Black contours on white background
                output_contour_frame = np.full((frame_height, frame_width), 255, dtype=np.uint8) # Start with white canvas
                cv2.drawContours(output_contour_frame, contours, -1, (0), 1) # Draw black contours
            
            return output_contour_frame
        else:
            # Fallback, should not be reached if __init__ validation is correct
            print(f"Warning: Unknown contour style '{self.contour_style}'. Returning grayscale frame.")
            return gray_frame
