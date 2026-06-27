# ColorSense - Smart Color Detection App

ColorSense is a beginner-friendly Python mini project that detects the dominant color from an uploaded image or a live webcam feed. It uses OpenCV, NumPy, Pillow, and Tkinter to provide a clean dark-themed desktop interface with history tracking and export tools.

## Features

- Modern dark Tkinter home screen
- Detect color from JPG, JPEG, and PNG images
- Live webcam detection using OpenCV
- Dominant color name, RGB, HEX, and coverage percentage
- Top five major colors in the image
- Color preview swatch and image preview
- Copy HEX code button
- Save detected color as PNG
- Save detections to CSV history
- View, refresh, export, and clear detection history
- Error handling for invalid images and unavailable webcams

## Project Structure

```text
ColorSense/
├── main.py
├── gui.py
├── image_detector.py
├── webcam_detector.py
├── color_utils.py
├── history.py
├── history.csv
├── assets/
├── screenshots/
├── README.md
└── requirements.txt
```

## Installation

1. Make sure Python 3.10 or newer is installed.
2. Open a terminal in the project folder.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

Tkinter is included with the standard Python distribution on Windows and macOS. On some Linux systems you may need to install it separately through your package manager.

## How It Works

- OpenCV reads the image or webcam frame.
- The frame is converted from BGR to RGB.
- The image is resized for faster processing.
- NumPy groups pixels into a compact palette and counts the most frequent colors.
- The closest named color is chosen by comparing the dominant RGB value with predefined color references.

## Usage

Run the application:

```bash
python main.py
```

### Image Detection

1. Click **Detect Color from Image**.
2. Upload a JPG, JPEG, or PNG file.
3. Review the preview, dominant color, RGB, HEX, top five colors, and coverage percentage.
4. Use **Copy HEX** or **Save Color as PNG** if needed.

### Webcam Detection

1. Click **Detect Color from Webcam**.
2. Allow camera access if your system asks for permission.
3. The app samples the live feed and updates the dominant color in real time.
4. Press **Q** to exit webcam mode.

### History

1. Click **View Detection History**.
2. Review detections inside the app.
3. Export the CSV file or clear the history if needed.

## Screenshots

Place screenshots in the `screenshots/` folder and reference them here. Suggested images:

- Home screen
- Image detection result
- Webcam detection result
- History window

## Notes

- `history.csv` is created automatically the first time the app runs.
- `pandas` is included as an optional dependency, but the app does not require it to run.
- The webcam mode saves sampled detections to history while it is running.
# ColorSense - Smart Color Detection App

ColorSense is a beginner-friendly Python mini project that detects the dominant color from an uploaded image or a live webcam feed. It uses OpenCV, NumPy, Pillow, and Tkinter to provide a clean dark-themed desktop interface with history tracking and export tools.

## Features

- Modern dark Tkinter home screen
- Detect color from JPG, JPEG, and PNG images
- Live webcam detection using OpenCV
- Dominant color name, RGB, HEX, and coverage percentage
- Top five major colors in the image
- Color preview swatch and image preview
- Copy HEX code button
- Save detected color as PNG
- Save detections to CSV history
- View, refresh, export, and clear detection history
- Error handling for invalid images and unavailable webcams

## Project Structure

```text
ColorSense/
├── main.py
├── gui.py
├── image_detector.py
├── webcam_detector.py
├── color_utils.py
├── history.py
├── history.csv
├── assets/
├── screenshots/
├── README.md
└── requirements.txt
```

## Installation

1. Make sure Python 3.10 or newer is installed.
2. Open a terminal in the project folder.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

Tkinter is included with the standard Python distribution on Windows and macOS. On some Linux systems you may need to install it separately through your package manager.

## How It Works

- OpenCV reads the image or webcam frame.
- The frame is converted from BGR to RGB.
- The image is resized for faster processing.
- NumPy is used to group pixels into a small palette and count the most frequent colors.
- The closest named color is chosen by comparing the dominant RGB value with predefined color references.

## Usage

Run the application:

```bash
python main.py
```

### Image Detection

1. Click **Detect Color from Image**.
2. Upload a JPG, JPEG, or PNG file.
3. Review the preview, dominant color, RGB, HEX, top five colors, and coverage percentage.
4. Use **Copy HEX** or **Save Color as PNG** if needed.

### Webcam Detection

1. Click **Detect Color from Webcam**.
2. Allow camera access if your system asks for permission.
3. The app samples the live feed and updates the dominant color in real time.
4. Press **Q** to exit webcam mode.

### History

1. Click **View Detection History**.
2. Review detections inside the app.
3. Export the CSV file or clear the history if needed.

## Screenshots

Place screenshots in the `screenshots/` folder and reference them here. Suggested images:

- Home screen
- Image detection result
- Webcam detection result
- History window

## Notes

- `history.csv` is created automatically the first time the app runs.
- `pandas` is included as an optional dependency, but the app does not require it to run.
- The webcam mode saves sampled detections to history while it is running.
