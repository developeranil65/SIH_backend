import { Router } from "express";
import {
  createPharma,
  getAllPharmas,
  getPharmaById,
  updatePharma,
  deletePharma,
} from "../controllers/pharma.controller.js";

const router = Router();

router.post("/", createPharma);
router.get("/", getAllPharmas);
router.get("/:id", getPharmaById);
router.put("/:id", updatePharma);
router.delete("/:id", deletePharma);

export default router;
