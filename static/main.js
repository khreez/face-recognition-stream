'use strict';

/* globals ImageCapture */

var imageCapture;
var mediaStream;

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
            const img = document.querySelector('img');
            img.src = URL.createObjectURL(blob);

            return createImageBitmap(blob);
        })
        .then(imageBitmap => {
            const canvas = document.querySelector('canvas');
            drawCanvas(canvas, imageBitmap);

            const label = document.querySelector('#labelField');

            var fd = new FormData();
            fd.append('image', canvas.toDataURL('image/jpeg'));
            fd.append('label', label.value);

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload');
            xhr.onreadystatechange = function () {
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