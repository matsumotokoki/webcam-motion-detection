const video = document.getElementById('video');
const canvas = document.createElement('canvas');
const form = document.getElementById('settings-form');

let lastImageData;

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        video.srcObject = stream;
        video.play();
    });
} else {
    alert("Sorry, your browser does not support access to the webcam.");
}

form.addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(form);

    fetch('/update_settings', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Settings updated successfully!');
        } else {
            alert('Failed to update settings.');
        }
    });
});

function detectMotion() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

    if (lastImageData) {
        const diff = getFrameDifference(lastImageData, imageData.data);
        const diffRatio = diff / (imageData.data.length / 4);

        if (diffRatio > parseFloat(form.threshold.value)) {
            const dataUrl = canvas.toDataURL('image/png');
            sendNotification(dataUrl);
        }
    }

    lastImageData = imageData.data;
}

function getFrameDifference(data1, data2) {
    let diff = 0;
    for (let i = 0; i < data1.length; i += 4) {
        const r = Math.abs(data1[i] - data2[i]);
        const g = Math.abs(data1[i + 1] - data2[i + 1]);
        const b = Math.abs(data1[i + 2] - data2[i + 2]);
        if (r > 20 || g > 20 || b > 20) { // Change sensitivity as needed
            diff++;
        }
    }
    return diff;
}

function sendNotification(dataUrl) {
    const imageData = dataUrl.split(',')[1]; // Extract base64 image data
    fetch('/notify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Notification sent successfully!');
        } else {
            console.error('Failed to send notification.');
        }
    });
}

setInterval(detectMotion, 1000); // Check for motion every second
