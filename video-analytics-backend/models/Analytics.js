// // models/Analytics.js
// const mongoose = require("mongoose");

// const analyticsSchema = new mongoose.Schema({
//   guestId: { type: String, required: true },
//   event: { type: String, required: true },
//   time: { type: Number, required: true },
//   additionalData: { type: Object, default: {} },
//   timestamp: { type: Date, default: Date.now },
// });

// module.exports = mongoose.model("Analytics", analyticsSchema);

const mongoose = require("mongoose");

const analyticsSchema = new mongoose.Schema({
  guestId: { type: String, required: true },
  event: { type: String, required: true },
  time: { type: Number, required: true },
  additionalData: { type: Object, default: {} },
  timestamp: { type: Date, default: Date.now },
});

module.exports = mongoose.model("Analytics", analyticsSchema);