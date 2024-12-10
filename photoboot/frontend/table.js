const socket = io(); // Connect to WebSocket server
const tableBody = document.getElementById('table-body'); // The table body in your HTML

let tableData = []; // This will hold the table data
let highlightedNumbers = new Set(); // Set to store all numbers that should remain yellow

// Function to fetch and render the table
async function fetchTableData() {
  try {
    const response = await fetch('/table');
    tableData = await response.json();
    renderTableRows();
  } catch (error) {
    console.error('Error fetching table data:', error);
  }
}

// Function to render table rows
function renderTableRows() {
  tableBody.innerHTML = ''; // Clear the existing table rows
  tableData.forEach(row => {
    const tr = document.createElement('tr');
    tr.dataset.number = row.number;

    // Determine cell style dynamically
    const numberCellStyle = getNumberCellStyle(row);

    tr.innerHTML = `
      <td class="number-cell" style="${numberCellStyle}">
        ${row.number}
      </td>
      <td><input type="checkbox" class="pc-toggle" data-number="${row.number}" data-field="pc1" ${row.pc1 ? 'checked' : ''}></td>
      <td><input type="checkbox" class="pc-toggle" data-number="${row.number}" data-field="pc2" ${row.pc2 ? 'checked' : ''}></td>
      <td><input type="text" class="file-name" data-number="${row.number}" value="${row.fileName}"></td>
      <td><input type="checkbox" class="printed-toggle" data-number="${row.number}" ${row.printed ? 'checked' : ''}></td>
      <td><input type="checkbox" class="express-toggle" data-number="${row.number}" ${row.express ? 'checked' : ''}></td>
      <td><input type="number" class="copies" data-number="${row.number}" value="${row.copies}"></td>
      <td><input type="text" class="notes" data-number="${row.number}" value="${row.notes}"></td>
    `;

    tableBody.appendChild(tr);
  });
}

// Function to get the style for the number cell
function getNumberCellStyle(row) {
  if (row.printed) {
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

// Event listener for toggles and inputs
tableBody.addEventListener('change', (event) => {
  const target = event.target;
  const rowNumber = parseInt(target.dataset.number, 10);

  if (rowNumber) {
    const row = tableData.find(r => r.number === rowNumber);
    if (!row) return;

    if (target.classList.contains('pc-toggle')) {
      const field = target.dataset.field;
      row[field] = target.checked;
    } else if (target.classList.contains('printed-toggle')) {
      row.printed = target.checked;
    } else if (target.classList.contains('express-toggle')) {
      row.express = target.checked;
    } else if (target.classList.contains('file-name')) {
      row.fileName = target.value;
    } else if (target.classList.contains('copies')) {
      row.copies = target.value;
    } else if (target.classList.contains('notes')) {
      row.notes = target.value;
    }

    // Remove number from highlightedNumbers if another toggle is activated
    if (row.pc1 || row.pc2 || row.printed || row.express) {
      highlightedNumbers.delete(row.number);
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
