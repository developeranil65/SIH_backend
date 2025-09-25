import { Router } from "express";
import {
  getLatestSummary,
  getDistrictTrend,
  getAllSummaries,
} from "../controllers/summary.controller.js";

const router = Router();

router.get("/latest", getLatestSummary); // Latest per district
router.get("/district/:district", getDistrictTrend); // Trends for one district
router.get("/", getAllSummaries); // Debug/all (paginated)

export default router;
