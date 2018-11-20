'use strict';

/* globals ImageCapture */

let imageCapture;
let mediaStream;

navigator.mediaDevices.getUserMedia({video: true})
    .then(stream => {
        mediaStream = stream;
        document.querySelector('video').srcObject = stream;
        imageCapture = new ImageCapture(stream.getVideoTracks()[0]);
    })
    .catch(error => console.log('error acquiring stream: ' + error));

function onTakePhotoButtonClick() {
    imageCapture.takePhoto()
        .then(blob => {
            let takePhotoButton = document.querySelector('#takePhotoButton');
            takePhotoButton.disabled = true;

            const canvas = document.querySelector('canvas');
            let bitmap = createImageBitmap(blob, {resizeQuality: "high", resizeWidth: 800, resizeHeight: 600});

            let label = document.querySelector('#labelField').value;
            label = label.toLowerCase();
            let fileName = label + '.jpg';

            const fd = new FormData();
            fd.append('image', blob, fileName);
            fd.append('label', label);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/capture');
            xhr.onreadystatechange = function () {
                takePhotoButton.disabled = false;
                if (xhr.readyState === 4 && xhr.status === 200) {
                    let response = JSON.parse(xhr.response);
                    bitmap.then(imageBitmap => drawCanvas(canvas, imageBitmap, response.filename));
                    document.querySelector('#enrollButton').classList.remove('hidden');
                } else {
                    drawText(canvas, 'something went wrong, unable to capture photo');
                }
            };
            xhr.send(fd);
        })
        .catch(error => console.log('error taking image' + error));
}

function onEnrollButtonClick() {
    let enrollButton = document.querySelector('#enrollButton');
    enrollButton.disabled = true;

    let takePhotoButton = document.querySelector('#takePhotoButton');
    takePhotoButton.disabled = true;

    const canvas = document.querySelector('canvas');
    drawText(canvas, 'processing facial enrollment...');

    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/enroll');
    xhr.onreadystatechange = function () {
        enrollButton.disabled = false;
        takePhotoButton.disabled = false;
        if (xhr.readyState === 4 && xhr.status === 200) {
            let response = JSON.parse(xhr.response);
            drawText(canvas, response.message);
        } else {
            drawText(canvas, 'something went wrong, unable complete facial enrollment')
        }
    };
    xhr.send();
}

function drawCanvas(canvas, img, filename) {
    canvas.width = getComputedStyle(canvas).width.split('px')[0];
    canvas.height = getComputedStyle(canvas).height.split('px')[0];
    let ratio = Math.min(canvas.width / img.width, canvas.height / img.height);
    let x = (canvas.width - img.width * ratio) / 2;
    let y = (canvas.height - img.height * ratio) / 2;

    let context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(img, 0, 0, img.width, img.height, x, y, img.width * ratio, img.height * ratio);
    context.font = '24px sans-serif';
    context.fillText(filename, 10, 10);
}

function drawText(canvas, message) {
    let context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.font = '24px sans-serif';
    context.fillText(message, 10, 10);
}

document.querySelector('#takePhotoButton').addEventListener('click', onTakePhotoButtonClick);
document.querySelector('#enrollButton').addEventListener('click', onEnrollButtonClick);
