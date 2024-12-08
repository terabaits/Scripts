const socket = io(); // Connect to the WebSocket server
const tableBody = document.getElementById('table-body');

// Fetch initial table data
const fetchTableData = async () => {
  const response = await fetch('/table');
  const data = await response.json();
  renderTable(data);
};

// Render the table rows
const renderTable = (data) => {
  tableBody.innerHTML = ''; // Clear existing rows

  data.forEach((row) => {
    const tr = document.createElement('tr');
    tr.dataset.number = row.number;

    // Add cells for each column
    tr.innerHTML = `
      <td>${row.number}</td>
      <td><button class="toggle-btn" data-field="pc1">${row.pc1 ? 'ON' : 'OFF'}</button></td>
      <td><button class="toggle-btn" data-field="pc2">${row.pc2 ? 'ON' : 'OFF'}</button></td>
      <td><input type="text" data-field="fileName" value="${row.fileName}"></td>
      <td><button class="toggle-btn" data-field="printed">${row.printed ? 'Printed' : 'Not Printed'}</button></td>
      <td><button class="toggle-btn" data-field="express">${row.express ? 'Express' : 'Normal'}</button></td>
      <td><input type="text" data-field="copies" value="${row.copies}"></td>
      <td><input type="text" data-field="notes" value="${row.notes}"></td>
    `;

    updateRowStyles(tr, row);
    tableBody.appendChild(tr);
  });
};

// Update styles for a row based on its state
const updateRowStyles = (tr, row) => {
  if (row.printed) {
    tr.style.backgroundColor = 'green';
  } else if (row.pc1 || row.pc2) {
    tr.style.backgroundColor = 'orange';
  } else if (row.number <= counterValue) { // Assuming `counterValue` is global
    tr.style.backgroundColor = 'yellow';
  } else {
    tr.style.backgroundColor = 'white';
  }
};

// Handle updates from the server
socket.on('table-update', ({ number, updates }) => {
  const row = document.querySelector(`tr[data-number="${number}"]`);
  if (row) {
    const rowData = tableData.find((r) => r.number === number);
    Object.assign(rowData, updates); // Update local data
    renderTable(tableData); // Re-render table to reflect changes
  }
});

// Handle user interactions
tableBody.addEventListener('change', async (e) => {
  const target = e.target;
  const tr = target.closest('tr');
  const number = parseInt(tr.dataset.number, 10);
  const field = target.dataset.field;

  const updates = { [field]: target.type === 'checkbox' ? target.checked : target.value };
  await fetch('/table/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ number, updates }),
  });
});

tableBody.addEventListener('click', async (e) => {
  if (e.target.classList.contains('toggle-btn')) {
    const tr = e.target.closest('tr');
    const number = parseInt(tr.dataset.number, 10);
    const field = e.target.dataset.field;

    const rowData = tableData.find((row) => row.number === number);
    const updates = { [field]: !rowData[field] }; // Toggle value
    await fetch('/table/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ number, updates }),
    });
  }
});

// Initialize table on page load
fetchTableData();
