const counterDisplay = document.getElementById('counter');
const decreaseButton = document.getElementById('decrease');
const increaseButton = document.getElementById('increase');

const socket = io(); // Connect to WebSocket server

// Update the counter display whenever the server sends an update
socket.on('counter-update', (value) => {
  counterDisplay.textContent = value;
});

// Function to update the counter via a server request
const updateCounter = async (change) => {
  await fetch('/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ change }),
  });
};

// Event listeners for button clicks
decreaseButton.addEventListener('click', () => updateCounter(-1));
increaseButton.addEventListener('click', () => updateCounter(1));

// Listen for keyboard events
document.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp') {
    updateCounter(1); // Increment counter when "+" key is pressed
  } else if (event.key === 'ArrowDown') {
    updateCounter(-1); // Decrement counter when "-" key is pressed
  }
});
