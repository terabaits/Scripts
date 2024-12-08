const counterDisplay = document.getElementById('counter');
const decreaseButton = document.getElementById('decrease');
const increaseButton = document.getElementById('increase');

const socket = io(); // Connect to WebSocket server

socket.on('counter-update', (value) => {
  counterDisplay.textContent = value;
});

const updateCounter = async (change) => {
  await fetch('/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ change }),
  });
};

decreaseButton.addEventListener('click', () => updateCounter(-1));
increaseButton.addEventListener('click', () => updateCounter(1));
