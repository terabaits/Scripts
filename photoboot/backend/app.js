const express = require('express');
const { Server } = require('socket.io');
const http = require('http');
const { sequelize, Counter } = require('./db');
const path = require('path');


const cors = require('cors');
const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

let counterValue = 0;

const PORT = 3003; // Keep PORT declaration here

console.log('Serving static files from:', path.join(__dirname, '../frontend'));

// In-memory table data for simplicity
let tableData = Array.from({ length: 90 }, (_, index) => ({
  number: index + 1,
  pc1: false,
  pc2: false,
  fileName: '',
  printed: false,
  express: false,
  copies: '',
  notes: '',
  highlighted: false, // track if the row should be highlighted
}));

// Sync database and initialize counter
(async () => {
  try {
    await sequelize.authenticate();
    await sequelize.sync();

    const [counter, created] = await Counter.findOrCreate({
      where: { id: 1 },
      defaults: { value: 0 },  // Ensure the counter has an initial value if not created
    });
    counterValue = counter.value;

    // Start the server after database is ready
    server.listen(PORT, '0.0.0.0', () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Error initializing the database:', error);
    process.exit(1);  // Exit if database fails to initialize
  }
})();

// API to update counter
app.post('/update', async (req, res) => {
  const { change } = req.body;
  counterValue += change;

  try {
    const counter = await Counter.findByPk(1);
    counter.value = counterValue;
    await counter.save();

    // Emit updated counter value to all connected clients
    io.emit('counter-update', counterValue);  // Emit the new counter value
    res.json({ value: counterValue });
  } catch (error) {
    console.error('Error updating counter:', error);
    res.status(500).json({ error: 'Failed to update counter' });
  }
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('A user connected');
  socket.emit('counter-update', counterValue);  // Emit current counter value on connection

  socket.on('disconnect', () => {
    console.log('A user disconnected');
  });

  // Listen for changes to the table data
  socket.on('table-update', (data) => {
    const { number, updates } = data;
    const rowIndex = tableData.findIndex((row) => row.number === number);

    if (rowIndex !== -1) {
      tableData[rowIndex] = { ...tableData[rowIndex], ...updates };
      io.emit('table-update', { number, updates }); // Emit updated table data to clients
    }
  });
});

// Endpoint to get the table data (persisted state)
app.get('/table', (req, res) => {
  res.json(tableData); // Return the current table data, including state and highlights
});

// Endpoint to update a specific row (persisted state)
app.post('/table/update', (req, res) => {
  const { number, updates } = req.body;
  const rowIndex = tableData.findIndex((row) => row.number === number);

  if (rowIndex !== -1) {
    tableData[rowIndex] = { ...tableData[rowIndex], ...updates };
    io.emit('table-update', { number, updates });
    res.json({ success: true, row: tableData[rowIndex] });
  } else {
    res.status(404).json({ success: false, error: 'Row not found' });
  }
});

app.post('/clear-table', (req, res) => {
  // Reset the in-memory tableData to its initial state
  tableData = tableData.map(row => ({
    number: row.number,
    pc1: false,
    pc2: false,
    fileName: '',
    printed: false,
    express: false,
    copies: '',
    notes: '',
    highlighted: false, // Ensure highlight state is also cleared
  }));

  io.emit('table-cleared'); // Notify all connected clients
  res.status(200).send('Table cleared successfully.');
});

