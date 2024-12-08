const express = require('express');
const { Server } = require('socket.io');
const http = require('http');
const { sequelize, Counter } = require('./db');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));


let counterValue = 0;

const PORT = 3003; // Keep PORT declaration here

console.log('Serving static files from:', path.join(__dirname, '../frontend'));


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
    server.listen(PORT, () => {
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

    io.emit('counter-update', counterValue);  // Emit updated counter value to all clients
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
});

let tableData = Array.from({ length: 90 }, (_, index) => ({
    number: index + 1,
    pc1: false,
    pc2: false,
    fileName: '',
    printed: false,
    express: false,
    copies: '',
    notes: '',
  }));
  
  // Endpoint to get the table data
  app.get('/table', (req, res) => {
    res.json(tableData);
  });
  
  // Endpoint to update a specific row
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
  
