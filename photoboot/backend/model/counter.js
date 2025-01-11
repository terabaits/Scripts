const { Sequelize } = require('sequelize');

// Database connection configuration
const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASSWORD, {
  host: process.env.DB_HOST,
  dialect: 'postgres',
  port: process.env.DB_PORT,
  logging: false,
});

// Function to establish a database connection with retries
async function connectWithRetry() {
  const maxRetries = 5;
  let attempt = 0;
  while (attempt < maxRetries) {
    try {
      console.log(`Attempt ${attempt + 1} to connect to the database...`);
      await sequelize.authenticate();
      console.log('Database connection established successfully!');
      break;
    } catch (error) {
      console.error(`Database connection failed: ${error.message}`);
      attempt++;
      if (attempt >= maxRetries) {
        console.error('Max retries reached. Exiting.');
        process.exit(1);
      }
      console.log('Retrying in 5 seconds...');
      await new Promise((res) => setTimeout(res, 5000));
    }
  }
}

connectWithRetry();

module.exports = sequelize;
