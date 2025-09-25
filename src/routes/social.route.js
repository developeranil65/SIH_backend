import { Router } from "express";
import {
  createSocialPost,
  getAllSocialPosts,
  getSocialPostById,
  updateSocialPost,
  deleteSocialPost,
} from "../controllers/social.controller.js";

const router = Router();

router.post("/", createSocialPost);
router.get("/", getAllSocialPosts);
router.get("/:id", getSocialPostById);
router.put("/:id", updateSocialPost);
router.delete("/:id", deleteSocialPost);

export default router;