const orb = document.querySelector('.glowing-orb');
const statusText = document.getElementById('status-text');

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
                statusText.textContent = 'listening...';
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
                } 

                const transcription = data.result;

                orb.classList.remove('recording');
                console.log('Recording stopped and processed:', data);
                orb.classList.add('thinking');
                statusText.textContent = 'reflecting...';
                // Call process_recording function
                return fetch('/delete_output', {method:'POST'})
                    .then(() => transcription); 
            })
            .then((transcription) => {
                return fetch('/process_recording', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ transcription: transcription }),
                });
            })
            .then(response => response.json())
            .then(processedData => {
                console.log('Recording processed:', processedData);
                isRecording = false;

                // Poll for new audio file
                const pollingInterval = setInterval(() => {
                    const timestamp = new Date().getTime(); // Create a unique timestamp
                    fetch(`/static/output.mp3?${timestamp}`, { method: 'HEAD' }) // Append the timestamp to the URL
                        .then(response => {
                            if (response.ok) {
                                clearInterval(pollingInterval); // Stop polling when file is available
                
                                // Play the new audio
                                const audio = new Audio(`/static/output.mp3?${timestamp}`); // Append timestamp here too
                                orb.classList.remove('thinking');
                                orb.classList.add('speaking');
                                statusText.textContent = '';
                
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
                            }
                        })
                        .catch(error => {
                            console.error('Error polling for new audio file:', error);
                        });
                }, 1000); // Poll every 1 second                
            })
            .catch(error => {
                console.error('Error during processing:', error);
                alert('An error occurred: ' + error.message);
                isRecording = false;
                orb.classList.remove('recording', 'thinking', 'speaking');
                statusText.textContent = '';
            });
    }
    }
);




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
