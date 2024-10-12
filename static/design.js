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
