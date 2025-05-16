// ======================
// server.js (Backend)
// ======================

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const app = express();

app.use(cors());
app.use(express.json());

mongoose.connect('mongodb://localhost:27017/psycho_test', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

const User = mongoose.model('User', {
  name: String,
  surname: String,
  age: Number,
  gender: String,
  region: String,
  createdAt: { type: Date, default: Date.now }
});

const Result = mongoose.model('Result', {
  userId: mongoose.Schema.Types.ObjectId,
  answers: [String],
  createdAt: { type: Date, default: Date.now }
});

const Admin = mongoose.model('Admin', {
  username: String,
  password: String
});

const SECRET_KEY = 'secret123';

app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;
  const admin = await Admin.findOne({ username });
  if (!admin || !(await bcrypt.compare(password, admin.password))) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const token = jwt.sign({ id: admin._id }, SECRET_KEY, { expiresIn: '1h' });
  res.json({ token });
});

function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.sendStatus(401);
  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    req.user = decoded;
    next();
  } catch {
    res.sendStatus(403);
  }
}

app.get('/api/users', authMiddleware, async (req, res) => {
  const users = await User.find();
  res.json(users);
});

app.get('/api/results', authMiddleware, async (req, res) => {
  const results = await Result.find().populate('userId');
  res.json(results);
});

app.post('/api/results', async (req, res) => {
  const { userId, answers } = req.body;
  const result = new Result({ userId, answers });
  await result.save();
  res.json({ success: true });
});

app.listen(5000, () => console.log('Server running on http://localhost:5000'));


// ==================================
// index.html (Frontend HTML layout)
// ==================================

<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Psychology Test Admin Panel</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h1>Admin Panel</h1>

  <input type="text" id="username" placeholder="Username">
  <input type="password" id="password" placeholder="Password">
  <button onclick="login()">Login</button>

  <h2>User Results</h2>
  <table id="results-table">
    <thead><tr><th>Name</th><th>Region</th><th>Age</th><th>Gender</th><th>Date</th></tr></thead>
    <tbody></tbody>
  </table>

  <h2>Region Stats</h2>
  <canvas id="regions-chart"></canvas>

  <h2>Age Stats</h2>
  <canvas id="ages-chart"></canvas>

  <h2>Gender Stats</h2>
  <canvas id="genders-chart"></canvas>

  <script src="script.js"></script>
</body>
</html>


// ======================
// script.js (Frontend JS)
// ======================

const API_BASE_URL = 'http://localhost:5000/api';

let token = '';

function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.token) {
      token = data.token;
      loadResults();
    } else {
      alert('Login failed');
    }
  });
}

function loadResults() {
  fetch(`${API_BASE_URL}/results`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(data => {
    const table = document.querySelector('#results-table tbody');
    table.innerHTML = '';

    const regions = {}, ages = {}, genders = {};

    data.forEach(r => {
      const user = r.userId;
      const row = `<tr><td>${user.name} ${user.surname}</td><td>${user.region}</td><td>${user.age}</td><td>${user.gender}</td><td>${new Date(r.createdAt).toLocaleDateString()}</td></tr>`;
      table.innerHTML += row;

      regions[user.region] = (regions[user.region] || 0) + 1;
      ages[user.age] = (ages[user.age] || 0) + 1;
      genders[user.gender] = (genders[user.gender] || 0) + 1;
    });

    drawChart('regions-chart', 'Users by Region', regions);
    drawChart('ages-chart', 'Users by Age', ages);
    drawChart('genders-chart', 'Users by Gender', genders);
  });
}

function drawChart(canvasId, label, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(data),
      datasets: [{
        label: label,
        data: Object.values(data),
        backgroundColor: 'rgba(54, 162, 235, 0.5)'
      }]
    }
  });
}
