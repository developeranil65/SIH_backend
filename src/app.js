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

// routes declaration

// Exporting the app to server.js
export {app}