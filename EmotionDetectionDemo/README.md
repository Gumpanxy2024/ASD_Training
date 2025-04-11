# Emotion Detection Project

This project is an emotion detection application that utilizes a webcam to capture video frames and predict emotions in real-time. It is built using Flask for the backend and JavaScript for handling camera access and emotion detection.

## Project Structure

```
emotion_detection
├── app.py                     # Main entry point of the application
├── static
│   ├── css
│   │   └── style.css          # CSS styles for the application
│   └── js
│       ├── camera.js          # Handles camera access and controls
│       └── detection.js       # Processes video frames for emotion detection
├── templates
│   ├── index.html             # Main HTML template for the application
│   └── result.html            # Displays results of emotion detection
├── models
│   └── emotion_model.h5       # Pre-trained emotion detection model
├── utils
│   ├── __init__.py            # Marks the utils directory as a Python package
│   └── emotion_detector.py     # Logic for loading the model and processing frames
├── requirements.txt            # Lists project dependencies
└── README.md                   # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd emotion_detection
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the Flask server by running:
   ```
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Usage

- Open the application in your web browser.
- Click the "开始检测" (Start Detection) button to begin capturing video and detecting emotions.
- Click the "停止检测" (Stop Detection) button to stop the detection and view the results.
- The results will display the recorded emotions along with their corresponding timestamps.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.