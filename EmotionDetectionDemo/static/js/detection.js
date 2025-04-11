// This file contains the logic for processing video frames from the camera, performing emotion detection using the model, and sending the results to the backend for logging.

let isDetecting = false;
let emotionData = [];

const startDetectionButton = document.getElementById('start-detection');
const stopDetectionButton = document.getElementById('stop-detection');

startDetectionButton.addEventListener('click', startDetection);
stopDetectionButton.addEventListener('click', stopDetection);

function startDetection() {
    isDetecting = true;
    emotionData = [];
    const hiddenVideo = document.getElementById('hidden-video');

    if (hiddenVideo) {
        hiddenVideo.play();
        detectEmotion(hiddenVideo);
    }
}

function stopDetection() {
    isDetecting = false;
    const result = JSON.stringify(emotionData);
    console.log(result);
    // Here you can send the result to the backend if needed
    // Example: fetch('/log-emotions', { method: 'POST', body: result });
}

function detectEmotion(videoElement) {
    if (!isDetecting) return;

    // Simulate emotion detection logic
    const emotion = getRandomEmotion(); // Replace with actual emotion detection logic
    const timestamp = new Date().toISOString();
    
    emotionData.push({ emotion, timestamp });

    // Call detectEmotion again for the next frame
    requestAnimationFrame(() => detectEmotion(videoElement));
}

function getRandomEmotion() {
    const emotions = ['happy', 'sad', 'angry', 'surprised', 'neutral'];
    return emotions[Math.floor(Math.random() * emotions.length)];
}