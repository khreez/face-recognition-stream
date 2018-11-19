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
            const canvas = document.querySelector('canvas');
            createImageBitmap(blob, {resizeQuality: "high", resizeWidth: 800, resizeHeight: 600})
                .then(imageBitmap => drawCanvas(canvas, imageBitmap));

            let label = document.querySelector('#labelField').value;
            label = label.toLowerCase();

            const fd = new FormData();
            fd.append('image', blob, label + '.jpg');
            fd.append('label', label);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload');
            xhr.onreadystatechange = function () {
                // error handling?
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log('image sent successfully');
                }
            };
            xhr.send(fd);
        })
        .catch(error => console.log('error taking image' + error));
}

function drawCanvas(canvas, img) {
    canvas.width = getComputedStyle(canvas).width.split('px')[0];
    canvas.height = getComputedStyle(canvas).height.split('px')[0];
    let ratio = Math.min(canvas.width / img.width, canvas.height / img.height);
    let x = (canvas.width - img.width * ratio) / 2;
    let y = (canvas.height - img.height * ratio) / 2;
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    canvas.getContext('2d').drawImage(img, 0, 0, img.width, img.height,
        x, y, img.width * ratio, img.height * ratio);
}

document.querySelector('video').addEventListener('play', function () {
    document.querySelector('#takePhotoButton').disabled = false;
});

document.querySelector('#takePhotoButton').addEventListener('click', onTakePhotoButtonClick);