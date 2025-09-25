import express from "express";
import cors from "cors";
import { ApiError } from "./utils/ApiError.js";

const app = express();

// Middlewares
app.use(cors({
    origin: process.env.CORS_ORIGIN,
    credentials: true
}));
app.use(express.json({
    limit: "16kb"
}));
app.use(express.urlencoded({
    extended: true, 
    limit: "16kb"
}));
app.use(express.static("public"));

app.use((err, req, res, next) => {
  if (err instanceof ApiError) {
    return res.status(err.statusCode).json({
      success: false,
      message: err.message,
      errors: err.errors,
    });
  }

  console.error(err);
  return res.status(500).json({
    success: false,
    message: "Internal Server Error",
  });
});

// routes import
import hospitalRoutes from "./routes/hospital.route.js";
import pharmaRoutes from "./routes/pharma.route.js";
import socialRoutes from "./routes/social.route.js";
import summaryRoutes from "./routes/summary.route.js";
import alertsRoutes from "./routes/alerts.route.js";

// routes declaration
app.use("/api/hospital", hospitalRoutes);
app.use("/api/pharma", pharmaRoutes);
app.use("/api/social", socialRoutes);
app.use("/api/summary", summaryRoutes);
app.use("/api/alerts", alertsRoutes);

// Exporting the app to server.js
export {app}