const express = require("express");
const fs = require("fs");
const cors = require("cors");
const path = require("path");

const app = express();
const PORT = 3000;

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json());

// ✅ Serve frontend static files - corrected path
app.use(express.static(path.join(__dirname, "../public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/autoencoder.html"));
});

// Log user behavior
app.post("/log", (req, res) => {
  const log = req.body;
  const threat = parseFloat(log.velocity) > 0.25 || log.touch_pressure > 0.9;
  fs.appendFileSync("server/activity_log.json", JSON.stringify(log) + "\n");
  res.json({ redirect_to_honeypot: threat });
});

app.listen(PORT, () => {
  console.log(`🌐 Website running at: http://localhost:${PORT}`);
});