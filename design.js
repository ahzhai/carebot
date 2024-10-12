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
    alert('Orb button clicked!');
    // Add your desired functionality here
});
