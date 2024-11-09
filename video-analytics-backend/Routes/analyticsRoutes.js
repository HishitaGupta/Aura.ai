// // routes/analyticsRoutes.js
// const express = require("express");
// const Analytics = require("../models/Analytics");

// const router = express.Router();

// // Endpoint to log analytics data
// router.post("/", async (req, res) => {
//   const { guestId, event, time, additionalData } = req.body;

//   if (!guestId) {
//     return res.status(400).json({ error: 'guestId is required' });
// }

//   try {
//     const newAnalytics = new Analytics({ guestId, event, time, additionalData });
//     await newAnalytics.save();
//     res.status(201).json({ message: "Analytics recorded successfully" });
//   } catch (error) {
//     console.error("Error saving analytics:", error);
//     res.status(500).json({ error: "Error saving analytics" });
//   }
//   res.status(200).json({ message: 'Analytics data received' });
// });

// module.exports = router;

const express = require("express");
const Analytics = require("../models/Analytics");

const router = express.Router();


router.get("/",(req,res)=>{
  res.send("Analytics server running");
})

// Endpoint to log analytics data
router.post("/", async (req, res) => {
  const { guestId, event, time, additionalData } = req.body;

  if (!guestId) {
    return res.status(400).json({ error: 'guestId is required' });
  }

  try {
    const newAnalytics = new Analytics({ guestId, event, time, additionalData });
    await newAnalytics.save();
    return res.status(201).json({ message: "Analytics recorded successfully" });
  } catch (error) {
    console.error("Error saving analytics:", error);
    return res.status(500).json({ error: "Error saving analytics" });
  }

  
});

module.exports = router;