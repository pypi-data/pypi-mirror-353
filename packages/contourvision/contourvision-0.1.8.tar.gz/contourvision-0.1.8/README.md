ContourVision: Video Contour Extraction Tool
ContourVision is a Python library for extracting and visualizing contours from video files. It offers various thresholding methods to highlight object outlines.

Core Features
* Multiple Thresholding Methods:
    * otsu: Automatic thresholding.
    * triangle: Statistical thresholding.
    * fixed: User-defined threshold value.
    * adaptive_mean: Neighborhood mean-based thresholding.
    * adaptive_gaussian: Weighted neighborhood Gaussian sum thresholding.
* Contour Styles:
    * white_on_black: White contours on a black background.
    * black_on_white: Black contours on a white background.
    * opencv_level_contours: Multi-level intensity contours with customizable colors.
* Processes video frames by first converting to grayscale.
* Finds external contours of objects.
* Simple class-based interface.

Installation
From PyPI (Once Published)

    pip install contourvision

From Source (for development)

    git clone [https://github.com/viliusbankauskas/contourvision.git](https://github.com/viliusbankauskas/contourvision.git)
    cd contourvision
    pip install -e .

Dependencies
* Python 3.8+
* OpenCV (opencv-python >= 4.0)
* NumPy (numpy >= 1.19)
(These are automatically installed via pip)

Quick Usage Example
    from contourvision import VideoContourExtractor
    import os

    input_video = "path/to/your/video.mp4" # Change this!
    output_dir = "processed_videos"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_video):
        print(f"Error: Input video '{input_video}' not found.")
    else:
        try:
            # Adaptive Gaussian thresholding, black contours on white
            output_adaptive_bw = os.path.join(output_dir, "result_adaptive_gaussian_bw.avi")
            extractor_adaptive = VideoContourExtractor(
                contour_style='black_on_white',
                threshold_type='adaptive_gaussian',
                adaptive_block_size=15, # Must be odd
                adaptive_c=5
            )
            print(f"Processing (Adaptive Gaussian): {input_video} -> {output_adaptive_bw}")
            extractor_adaptive.process_video(input_video, output_adaptive_bw)
            print(f"Finished: {output_adaptive_bw}")

            # Level contours example
            output_level = os.path.join(output_dir, "result_level_contours_green.avi")
            extractor_level = VideoContourExtractor(
                contour_style='opencv_level_contours',
                num_levels=5,
                level_contour_color=(0, 255, 0), # Green contours
                level_background_color=(30, 30, 30) # Dark gray background
            )
            print(f"Processing (Level Contours): {input_video} -> {output_level}")
            extractor_level.process_video(input_video, output_level)
            print(f"Finished: {output_level}")

            print(f"\nProcessing complete. Outputs in '{output_dir}'.")

        except Exception as e:
            print(f"An error occurred: {e}")

Remember to replace "path/to/your/video.mp4".

VideoContourExtractor Key Parameters
* contour_style (str): 'white_on_black' (default), 'black_on_white', 'opencv_level_contours'.
* threshold_type (str): 'otsu' (default), 'triangle', 'fixed', 'adaptive_mean', 'adaptive_gaussian'.
* threshold_value (int): For threshold_type='fixed'. Default: 127.
* adaptive_block_size (int): For adaptive methods (odd, >1). Default: 11.
* adaptive_c (int/float): Constant for adaptive methods. Default: 2.
* num_levels (int): For opencv_level_contours. Default: 5.
* explicit_levels (list): Specific levels for opencv_level_contours. Overrides num_levels.
* level_contour_color (tuple BGR): Color for opencv_level_contours. Default: (0,0,0).
* level_background_color (tuple BGR): Background for opencv_level_contours. Default: (255,255,255).
* invert_level_output (bool): Invert colors for opencv_level_contours. Default: False.

Running Examples
* Comprehensive Tests: See examples/test2.py. It creates a dummy video if needed and showcases various features.

    python examples/test2.py

Outputs are in examples/output_videos_from_test/.
* Basic Example: See examples/run_contour_detection.py for a simpler demonstration.

    python examples/run_contour_detection.py

Outputs are in examples/output_videos/.

Future Enhancements
* Draw contours directly on original color frames (on_original style).
* Contour customization (thickness, type like cv2.RETR_LIST).
* Command-Line Interface (CLI).
* Performance optimizations.
* Enhanced error handling and logging.
* Comprehensive unit tests.
* Dedicated documentation site (Sphinx/MkDocs).
* More output video formats/codec options.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Contributions are welcome! Please submit a pull request or open an issue.