const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize('counterdb', 'user', 'password', {
  host: 'db', // Docker service name for PostgreSQL
  dialect: 'postgres',
});

const Counter = sequelize.define('Counter', {
  value: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
  },
});

module.exports = { sequelize, Counter };
