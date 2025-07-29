import cv2
import numpy as np
import os

class VideoContourExtractor:
    """
    A class for extracting contours from video frames using different methods.
    """
    def __init__(self, 
                 threshold_type='otsu', 
                 contour_style='white_on_black',
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
            threshold_type (str): The thresholding method for OpenCV 'binary' styles.
                                  Currently supports 'otsu'.
            contour_style (str): The style of the output contours.
                                 'white_on_black' - OpenCV contours on black background.
                                 'black_on_white' - OpenCV contours on white background.
                                 'opencv_level_contours' - Contours at multiple intensity levels using OpenCV.
            
            For 'opencv_level_contours' style:
            num_levels (int): Number of intensity levels to find contours at if explicit_levels is None.
            explicit_levels (list of int, optional): Specific intensity levels (0-255) to find contours at.
            level_contour_color (tuple BGR): Color of the contour lines for 'opencv_level_contours'.
            level_background_color (tuple BGR): Background color for 'opencv_level_contours'.
            invert_level_output (bool): If True, inverts the final output colors for 'opencv_level_contours'.
        """
        self.threshold_type = threshold_type.lower()
        self.contour_style = contour_style.lower()

        # Store parameters for 'opencv_level_contours'
        self.num_levels = num_levels
        self.explicit_levels = explicit_levels
        self.level_contour_color = level_contour_color
        self.level_background_color = level_background_color
        self.invert_level_output = invert_level_output

        supported_binary_styles = ['white_on_black', 'black_on_white']
        supported_level_styles = ['opencv_level_contours']
        all_styles = supported_binary_styles + supported_level_styles

        if self.contour_style not in all_styles:
            raise ValueError(f"Unsupported 'contour_style'. Supported values: {', '.join(all_styles)}.")

        if self.contour_style in supported_binary_styles:
            if not isinstance(threshold_type, str) or self.threshold_type not in ['otsu']:
                raise ValueError(f"Unsupported 'threshold_type' for '{self.contour_style}'. Supported value: 'otsu'.")
        
        if self.contour_style in supported_level_styles:
            if not isinstance(self.num_levels, int) or self.num_levels < 1:
                raise ValueError("'num_levels' must be a positive integer.")
            if self.explicit_levels is not None:
                if not isinstance(self.explicit_levels, list) or not all(isinstance(lvl, int) and 0 <= lvl <= 255 for lvl in self.explicit_levels):
                    raise ValueError("'explicit_levels' must be a list of integers between 0 and 255.")
        
        print(f"VideoContourExtractor initialized: style='{self.contour_style}'")
        if self.contour_style in supported_binary_styles:
            print(f"  OpenCV threshold='{self.threshold_type}'")
        elif self.contour_style in supported_level_styles:
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
            
            is_color_output = self.contour_style == 'opencv_level_contours'
            
            output_dir = os.path.dirname(output_video_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=is_color_output)

            print(f"Starting video processing: '{input_video_path}' -> '{output_video_path}' (Style: {self.contour_style})")
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Total frames to process: {total_frames if total_frames > 0 else 'N/A'}")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break 

                processed_frame = self._process_frame(frame, frame_width, frame_height)
                out.write(processed_frame)
                frame_count += 1
                if frame_count % 100 == 0 and total_frames > 0: 
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
                    levels_to_process = np.linspace(min_val, max_val, self.num_levels + 2, dtype=int)[1:-1] # Exclude absolute min/max for better visual
                    if not levels_to_process.any() and self.num_levels >=1: # if linspace gives empty for some reason with few levels
                        levels_to_process = [int((min_val + max_val) / 2)]


            # Create a BGR canvas for drawing colored contours
            output_canvas = np.full((frame_height, frame_width, 3), self.level_background_color, dtype=np.uint8)

            for level in levels_to_process:
                # For each level, threshold the image.
                # Pixels >= level become white, others black.
                # This helps find lines where intensity crosses this level.
                _, binary_at_level = cv2.threshold(gray_frame, int(level), 255, cv2.THRESH_BINARY)
                
                # Find contours on this thresholded image
                # RETR_LIST retrieves all contours without establishing hierarchical relationships.
                # CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments.
                contours, _ = cv2.findContours(binary_at_level, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                
                # Draw these contours on the output canvas
                cv2.drawContours(output_canvas, contours, -1, self.level_contour_color, 1) # thickness 1

            if self.invert_level_output:
                output_canvas = 255 - output_canvas
            
            return output_canvas

        elif self.contour_style in ['white_on_black', 'black_on_white']:
            if self.threshold_type == 'otsu':
                thresh_mode = cv2.THRESH_BINARY_INV if self.contour_style == 'white_on_black' else cv2.THRESH_BINARY
                _, binary_image = cv2.threshold(gray_frame, 0, 255, thresh_mode + cv2.THRESH_OTSU)
            else:
                print(f"Warning: Unsupported threshold type '{self.threshold_type}' for OpenCV style. Defaulting to THRESH_BINARY_INV + OTSU.")
                _, binary_image = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if self.contour_style == 'white_on_black':
                output_contour_frame = np.zeros((frame_height, frame_width), dtype=np.uint8)
                cv2.drawContours(output_contour_frame, contours, -1, (255), 1)
            else: # black_on_white
                output_contour_frame = np.full((frame_height, frame_width), 255, dtype=np.uint8)
                cv2.drawContours(output_contour_frame, contours, -1, (0), 1)
            return output_contour_frame
        else:
            print(f"Warning: Unknown contour style '{self.contour_style}'. Defaulting to white on black.")
            _, binary_image = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) # Fallback
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            output_contour_frame = np.zeros((frame_height, frame_width), dtype=np.uint8)
            cv2.drawContours(output_contour_frame, contours, -1, (255), 1)
            return output_contour_frame
