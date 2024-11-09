// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const analyticsRoutes = require("./Routes/analyticsRoutes");

const app = express();

// Updated CORS configuration to allow requests from your Vite dev server
app.use(cors({
  origin: ["http://localhost:5173", "http://localhost:5000"], // Add both development and production origins
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));

app.use(express.json());

// MongoDB Connection
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    console.log("Connected to MongoDB");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    process.exit(1);
  }
};

connectDB();

// Add a test route to verify server is responding
app.get('/api/test', (req, res) => {
  res.json({ message: 'Server is running correctly' });
});

// Routes
app.use("/api/analytics", analyticsRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});