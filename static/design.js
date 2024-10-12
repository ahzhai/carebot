const orb = document.querySelector('.glowing-orb');

orb.addEventListener('mouseover', () => {
    orb.style.boxShadow = `
        0 0 20px #ffcc99,
        0 0 40px #ffcc99,
        0 0 60px #ff9933,
        0 0 80px #ff9933
    `;
});

orb.addEventListener('mouseout', () => {
    orb.style.boxShadow = `
        0 0 20px #ff9999,
        0 0 40px #ff9999,
        0 0 60px #ff3366,
        0 0 80px #ff3366
    `;
});

let isRecording = false;

orb.addEventListener('click', () => {
    if (!isRecording) {
        // First click: Start recording
        fetch('/start_recording')
            .then(response => response.json())
            .then(data => {
                console.log('Recording started:', data);
                isRecording = true;
                orb.classList.add('recording');
            })
            .catch(error => {
                console.error('Error starting recording:', error);
            });
    } else {
        // Second click: Stop recording and process audio file
        fetch('/stop_recording')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error stopping recording:', data.error);
                    alert('Error stopping recording: ' + data.error);
                } else {
                    orb.classList.remove('recording');
                    console.log('Recording stopped and processed:', data);
                    orb.classList.add('thinking');
                    // Call process_recording function
                    return fetch('/process_recording', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ transcription: data.result }),
                    });
                }
            })
            .then(response => response.json())
            .then(processedData => {
                console.log('Recording processed:', processedData);
                isRecording = false;
                // orb.classList.add('normal');

                // Play the audio file
                console.log('Creating audio player');
                // Update the audio file path
                fetch('/static/temp.mp3')
                    .then(response => {
                        if (response.ok) {
                            const audio = new Audio('/static/temp.mp3');
                            orb.classList.remove('thinking');
                            orb.classList.add('speaking');

                            audio.addEventListener('play', () => {
                                orb.style.animationDuration = `${audio.duration * 0.001}s`;
                            });

                            audio.addEventListener('ended', () => {
                                orb.classList.remove('speaking');
                            });

                            audio.play().catch(error => {
                                console.error('Error playing audio:', error);
                                alert('Error playing audio: ' + error.message);
                                orb.classList.remove('speaking');
                            });
                        } else {
                            throw new Error('Audio file not found');
                        }
                    })
                    .catch(error => {
                        console.error('Error loading audio file:', error);
                        alert('Error loading audio file: ' + error.message);
                    });
            })
            .catch(error => {
                console.error('Error processing recording:', error);
                alert('Error processing recording: ' + error.message);
                isRecording = false;
                orb.classList.remove('recording');
            });
    }
});




/*
orb.addEventListener('click', () => {
    fetch('/calculate', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Result:', data.result);
        alert(`The result of the calculation is: ${data.result}`);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while calculating.');
    });
});
*/
