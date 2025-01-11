const socket = io(); // Connect to WebSocket server
socket.on('connect', () => {
  console.log('WebSocket connected');
});
const tableBody = document.getElementById('table-body'); // The table body in your HTML

let tableData = []; // This will hold the table data
let highlightedNumbers = new Set(); // Set to store all numbers that should remain yellow

const saveButton = document.getElementById('save-button');
const clearButton = document.getElementById('clear-button');
const counterDisplay = document.getElementById('counter');
const decreaseButton = document.getElementById('decrease');
const increaseButton = document.getElementById('increase');

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

saveButton.addEventListener('click', () => {
    if (tableData.length === 0) {
      alert("No data to save!"); // Notify if there's no data
      return;
    }
  
    const wb = XLSX.utils.book_new(); // Create a new workbook
    const wsData = [
      ['Number', 'PC1', 'PC2', 'Printed', 'Express', 'Paid', 'Picked', 'Payment Type', 'Price', 'People Count', 'Copies', 'Notes'], // Header row
      ...tableData.map(row => [
        row.number || '',
        row.pc1 ? 'Yes' : 'No',
        row.pc2 ? 'Yes' : 'No',
        row.printed ? 'Yes' : 'No',
        row.express ? 'Yes' : 'No',
        row.paid ? 'Yes' : 'No',
        row.picked ? 'Yes' : 'No',
        row.upload ? 'Yes' : 'No', // Include the Upload column
        row.paymentType || '',
        row.price || '',
        row.peopleCount || 0,
        row.copies || 0,
        row.notes || ''
      ]),
    ];
    
  
    try {
      const ws = XLSX.utils.aoa_to_sheet(wsData); // Convert data to worksheet
      XLSX.utils.book_append_sheet(wb, ws, 'Table Data'); // Add worksheet to workbook
      XLSX.writeFile(wb, 'table_data.xlsx'); // Trigger the file download
      alert("Data saved successfully!");
    } catch (error) {
      console.error("Error saving data:", error);
      alert("Failed to save data.");
    }
  });

// Function to clear all fields and colors
clearButton.addEventListener('click', () => {
  // Clear all table fields
  tableData.forEach(row => {
    row.letter = '';
    row.pc1 = false;
    row.pc2 = false;
    row.fileName = '';
    row.printed = false;
    row.express = false;
    row.copies = 0;
    row.notes = '';
  });

  // Clear all highlights
  highlightedNumbers.clear();

  // Send the cleared data to the server
  fetch('/clear-table', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(tableData), // Send updated table data to the server
  })
    .then(response => {
      if (response.ok) {
        console.log('Table cleared on the server.');
      } else {
        console.error('Failed to clear table on the server.');
      }
    })
    .catch(error => console.error('Error clearing table:', error));

  // Re-render the table locally
  renderTableRows();
});

socket.on('table-cleared', () => {
  // Clear the table UI
  const tbody = document.getElementById('table-body');
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }

  // Optionally, you can re-fetch the updated table state
  fetch('/table')
    .then(response => response.json())
    .then(data => {
      populateTable(data); // Assuming you have a function to populate the table
      console.log(data);
    });
});

// Function to fetch and render the table
async function fetchTableData() {
  try {
    const response = await fetch('/table');
    tableData = await response.json();
    console.log('Fetched table data:', tableData); // Debug fetched data
    renderTableRows();
  } catch (error) {
    console.error('Error fetching table data:', error);
  }
}

// Function to render table rows
function renderTableRows() {
  tableBody.innerHTML = ''; // Clear existing rows
  tableData.forEach(row => {
    const tr = document.createElement('tr');
    tr.dataset.number = row.number;

    const numberCellStyle = getNumberCellStyle(row); // Dynamic cell style

    tr.innerHTML = `
      <td class="number-cell" style="${numberCellStyle}">
        ${row.number}
      </td>
      <td class="letter-cell">
        <select class="letter-dropdown" data-number="${row.number}">
          <option value="" ${row.letter === '' ? 'selected' : ''}>Select</option>
          ${Array.from({ length: 26 }, (_, i) => {
            const letter = String.fromCharCode(65 + i);
            return `<option value="${letter}" ${row.letter === letter ? 'selected' : ''}>${letter}</option>`;
          }).join('')}
        </select>
      </td>
      <td><input type="checkbox" class="pc-toggle" data-number="${row.number}" data-field="pc1" ${row.pc1 ? 'checked' : ''}></td>
      <td><input type="checkbox" class="pc-toggle" data-number="${row.number}" data-field="pc2" ${row.pc2 ? 'checked' : ''}></td>
      <td><input type="checkbox" class="printed-toggle" data-number="${row.number}" ${row.printed ? 'checked' : ''}></td>
      <td><input type="checkbox" class="express-toggle" data-number="${row.number}" ${row.express ? 'checked' : ''}></td>
      <td><input type="checkbox" class="paid-toggle" data-number="${row.number}" ${row.paid ? 'checked' : ''}></td>
      <td><input type="checkbox" class="picked-toggle" data-number="${row.number}" ${row.picked ? 'checked' : ''}></td>
      <td><input type="checkbox" class="upload-toggle" data-number="${row.number}" ${row.upload ? 'checked' : ''}></td>
      <td><input type="text" class="price" data-number="${row.number}" value="${row.price || ''}"></td>
      <td>
        <select class="payment-type" data-number="${row.number}">
          <option value="" ${row.paymentType === '' ? 'selected' : ''}>Select</option>
          <option value="Cash" ${row.paymentType === 'Cash' ? 'selected' : ''}>Cash</option>
          <option value="Card" ${row.paymentType === 'Card' ? 'selected' : ''}>Card</option>
        </select>
      </td>
      <td><input type="number" class="people-count" data-number="${row.number}" value="${row.peopleCount || 0}"></td>
      <td><input type="number" class="copies" data-number="${row.number}" value="${row.copies}"></td>
      <td><input type="text" class="notes" data-number="${row.number}" value="${row.notes}"></td>
    `;

    tableBody.appendChild(tr);
  });
}


// Function to get the style for the number cell
function getNumberCellStyle(row) {
  if (row.paid) {
    return 'background-color: blue; color: white;';
  } else if (row.picked) {
    return 'background-color: lightblue; color: black;';
  } else if (row.printed) {
    return 'background-color: green; color: black;';
  } else if (row.express) {
    return 'background-color: red; color: white;';
  } else if (row.pc1 || row.pc2) {
    return 'background-color: orange; color: black;';
  } else if (highlightedNumbers.has(row.number)) {
    return 'background-color: yellow; color: black;';
  }
  return ''; // Default style
}


tableBody.addEventListener('change', (event) => {
  const target = event.target;
  const rowNumber = parseInt(target.dataset.number, 10);

  if (rowNumber) {
    const row = tableData.find(r => r.number === rowNumber);
    if (!row) return;

    if (target.classList.contains('letter-dropdown')) {
      row.letter = target.value;
    } else if (target.classList.contains('pc-toggle')) {
      const field = target.dataset.field;
      row[field] = target.checked;
    } else if (target.classList.contains('printed-toggle')) {
      row.printed = target.checked;
    } else if (target.classList.contains('express-toggle')) {
      row.express = target.checked;
    } else if (target.classList.contains('copies')) {
      row.copies = target.value;
    } else if (target.classList.contains('notes')) {
      row.notes = target.value;
    } else if (target.classList.contains('paid-toggle')) {
      row.paid = target.checked;
      if (row.paid) row.picked = false; // Uncheck Picked if Paid is checked
    } else if (target.classList.contains('picked-toggle')) {
      row.picked = target.checked;
      if (row.picked) row.paid = false; // Uncheck Paid if Picked is checked
    } else if (target.classList.contains('upload-toggle')) {
      row.upload = target.checked; // Update the upload status
    } else if (target.classList.contains('payment-type')) {
      row.paymentType = target.value; // Update payment type 
    } else if (target.classList.contains('price')) {
      row.price = target.value;
    } else if (target.classList.contains('people-count')) {
      row.peopleCount = target.value;
    }

    // Emit the updated row to the server
    socket.emit('table-update', { number: row.number, updates: row });

    renderTableRows(); // Re-render rows to apply new styles
  }
});


// Listen for counter updates and add the corresponding number to highlightedNumbers
socket.on('counter-update', (counterValue) => {
  highlightedNumbers.add(counterValue); // Add the counter number to highlightedNumbers
  renderTableRows(); // Re-render rows to apply updated styles
});

// Listen for table updates from the WebSocket
socket.on('table-update', ({ number, updates }) => {
  const row = tableData.find(r => r.number === number);
  if (row) {
    Object.assign(row, updates); // Merge updates into the row
    renderTableRows(); // Re-render rows to apply new styles
  }
});

// Initialize the table data when the page loads
window.onload = fetchTableData;
