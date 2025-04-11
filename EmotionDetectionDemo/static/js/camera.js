// This file handles the camera access and controls for starting and stopping the video stream. 
// It interacts with the HTML elements to manage the user interface.

const videoElement = document.getElementById('hidden-video');
const startButton = document.getElementById('start-detection');
const stopButton = document.getElementById('stop-detection');
let isDetecting = false;
let emotionData = [];

// Function to start video stream
function startVideoStream() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                videoElement.srcObject = stream;
                isDetecting = true;
                startEmotionDetection();
            })
            .catch(function(error) {
                console.error("无法访问摄像头: ", error);
            });
    }
}

// Function to stop video stream
function stopVideoStream() {
    const stream = videoElement.srcObject;
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        videoElement.srcObject = null;
    }
    isDetecting = false;
    sendEmotionDataToServer();
}

// Function to start emotion detection
function startEmotionDetection() {
    if (isDetecting) {
        setInterval(() => {
            analyzeVideoFrame(videoElement);
        }, 1000);
    }
}

// Function to analyze video frame and simulate emotion detection
function analyzeVideoFrame(videoElement) {
    // Simulate emotion detection logic
    const emotions = ['happy', 'sad', 'angry', 'surprised'];
    const detectedEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    const timestamp = new Date().toISOString();

    // Store detected emotion and timestamp
    emotionData.push({ emotion: detectedEmotion, time: timestamp });
}

// Function to send emotion data to the server
function sendEmotionDataToServer() {
    fetch('/log-emotions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(emotionData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Emotion data logged:', data);
    })
    .catch((error) => {
        console.error('Error logging emotion data:', error);
    });
}

// Event listeners for buttons
startButton.addEventListener('click', startVideoStream);
stopButton.addEventListener('click', stopVideoStream);