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



// Endpoint to fetch analytics data
router.get("/", async (req, res) => {
  try {
    // Fetch data from MongoDB
    const analyticsData = await Analytics.find();
    res.status(200).json(analyticsData);
  } catch (error) {
    res.status(500).json({ message: "Error fetching analytics data", error });
  }
});



// router.get("/",(req,res)=>{
//   res.send("Analytics server running");
// })

// Endpoint to log analytics data
// router.post("/", async (req, res) => {
  
//   const { guestId, event, time, additionalData } = req.body;

//   if (!guestId) {
//     return res.status(400).json({ error: 'guestId is required' });
//   }

//   try {
//     const newAnalytics = new Analytics({ guestId, event, time, additionalData });
//     await newAnalytics.save();
//     return res.status(201).json({ message: "Analytics recorded successfully" });
//   } catch (error) {
//     console.error("Error saving analytics:", error);
//     return res.status(500).json({ error: "Error saving analytics" });
//   }

  
// });

const axios = require("axios");


// Replace with your actual IP geolocation API token
const GEOLOCATION_API_TOKEN = "71396080e1a39d";

router.post("/", async (req, res) => {
  const { guestId, event, time, additionalData = {} } = req.body;

  if (!guestId) {
    return res.status(400).json({ error: 'guestId is required' });
  }

  try {
    // Try to get the client IP address
    const userIp = req.headers["x-forwarded-for"] || req.connection.remoteAddress;
    console.log("Client IP:", userIp);

    // Check if IP is localhost
    if (userIp === "::1" || userIp === "127.0.0.1") {
      console.log("Running locally, unable to fetch external location data.");
      additionalData.location = { ip: userIp, message: "Localhost IP, no geolocation available" };
    } else {
      // Fetch location data
      const locationResponse = await axios.get(`https://ipinfo.io/${userIp}?token=${GEOLOCATION_API_TOKEN}`);
      const locationData = locationResponse.data;

      additionalData.location = {
        city: locationData.city,
        region: locationData.region,
        country: locationData.country,
        ip: userIp,
      };
    }

    // Save analytics to the database
    const newAnalytics = new Analytics({ guestId, event, time, additionalData });
    await newAnalytics.save();

    return res.status(201).json({ message: "Analytics recorded successfully" });
  } catch (error) {
    console.error("Error saving analytics:", error);
    return res.status(500).json({ error: "Error saving analytics" });
  }
});


module.exports = router;