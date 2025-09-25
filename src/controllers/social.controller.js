import { prisma } from "../utils/prisma.js";
import { ApiError } from "../utils/ApiError.js";
import { ApiResponse } from "../utils/ApiResponse.js";

// Create Social Post
export const createSocialPost = async (req, res, next) => {
  try {
    const { platform, content, district, sentiment, reach } = req.body;

    if (!platform || !content || !district) {
      throw new ApiError(400, "platform, content and district are required");
    }

    const post = await prisma.socialPost.create({
      data: { platform, content, district, sentiment, reach },
    });

    res.status(201).json(new ApiResponse(201, post, "Social post created successfully"));
  } catch (err) {
    next(err);
  }
};

// Get All Social Posts (latest 50)
export const getAllSocialPosts = async (req, res, next) => {
  try {
    const posts = await prisma.socialPost.findMany({
      orderBy: { createdAt: "desc" },
      take: 50,
    });
    res.json(new ApiResponse(200, posts, "Social posts fetched successfully"));
  } catch (err) {
    next(err);
  }
};

// Get Social Post by ID
export const getSocialPostById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const post = await prisma.socialPost.findUnique({ where: { id } });

    if (!post) throw new ApiError(404, "Social post not found");

    res.json(new ApiResponse(200, post, "Social post fetched successfully"));
  } catch (err) {
    next(err);
  }
};

// Update Social Post
export const updateSocialPost = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { platform, content, district, sentiment, reach } = req.body;

    const post = await prisma.socialPost.update({
      where: { id },
      data: { platform, content, district, sentiment, reach },
    });

    res.json(new ApiResponse(200, post, "Social post updated successfully"));
  } catch (err) {
    next(err);
  }
};

// Delete Social Post
export const deleteSocialPost = async (req, res, next) => {
  try {
    const { id } = req.params;

    await prisma.socialPost.delete({ where: { id } });

    res.json(new ApiResponse(200, null, "Social post deleted successfully"));
  } catch (err) {
    next(err);
  }
};
