const express = require('express');
const sqlite3 = require('better-sqlite3');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

// Initialize server and database
const app = express();
const db = new sqlite3('./counter.db');
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Database
db.exec(`CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, value INTEGER)`);

// Initialize the counter with a value of 0 if not present
const row = db.prepare('SELECT * FROM counter WHERE id = 1').get();
if (!row) {
  db.prepare('INSERT INTO counter (id, value) VALUES (1, 0)').run();
}

// API Endpoints
app.get('/counter', (req, res) => {
  const { value } = db.prepare('SELECT value FROM counter WHERE id = 1').get();
  res.json({ count: value });
});

// Route to update counter (increase or decrease)
app.post('/counter', (req, res) => {
  const { increment } = req.body;

  if (typeof increment !== 'boolean') {
    return res.status(400).json({ error: 'Increment should be a boolean' });
  }

  // Update the counter value
  db.prepare('UPDATE counter SET value = value + ? WHERE id = 1').run(increment ? 1 : -1);
  
  // Get the updated counter value
  const { value } = db.prepare('SELECT value FROM counter WHERE id = 1').get();
  
  // Emit the updated value to all connected clients
  io.emit('counter-update', value);

  // Return the updated counter value
  res.json({ count: value });
});

// WebSocket Handling
io.on('connection', (socket) => {
  console.log('A user connected');
  
  // Emit the current counter value to the newly connected client
  const { value } = db.prepare('SELECT value FROM counter WHERE id = 1').get();
  socket.emit('counter-update', value);

  socket.on('disconnect', () => {
    console.log('A user disconnected');
  });
});

// Start Server
const PORT = 3003;
server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
