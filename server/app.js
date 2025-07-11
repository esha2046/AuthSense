const express = require("express");
const fs = require("fs");
const cors = require("cors");
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

app.post("/log", (req, res) => {
  const log = req.body;

  // Basic threat detection (for example purposes)
  const threat = parseFloat(log.velocity) > 0.25 || log.touch_pressure > 0.9;

  fs.appendFileSync("server/activity_log.json", JSON.stringify(log) + "\n");

  res.json({ redirect_to_honeypot: threat });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
