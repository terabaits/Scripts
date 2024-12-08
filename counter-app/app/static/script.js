const counterDisplay = document.getElementById("counter-display");
const incrementButton = document.getElementById("increment");
const decrementButton = document.getElementById("decrement");

const fetchCounter = async () => {
    try {
        const response = await fetch('/counter');
        if (response.ok) {
            const data = await response.json();
            counterDisplay.textContent = data.value;
        } else {
            console.error('Failed to fetch counter:', response.status);
        }
    } catch (error) {
        console.error('Error fetching counter:', error);
    }
};

const updateCounter = async (delta) => {
    try {
        const response = await fetch('/counter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ delta }),
        });
        if (response.ok) {
            const data = await response.json();
            counterDisplay.textContent = data.value;
        } else {
            console.error('Failed to update counter:', response.status);
        }
    } catch (error) {
        console.error('Error updating counter:', error);
    }
};

// Event listeners for buttons
incrementButton.addEventListener("click", () => updateCounter(1));
decrementButton.addEventListener("click", () => updateCounter(-1));

// Initialize counter on page load
fetchCounter();
