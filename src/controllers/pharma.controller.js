import { prisma } from "../utils/prisma.js";
import { ApiError } from "../utils/ApiError.js";
import { ApiResponse } from "../utils/ApiResponse.js";

// Create Pharma
export const createPharma = async (req, res, next) => {
  try {
    const { name, address, city, state, pincode, contact } = req.body;

    if (!name || !address || !city || !state || !pincode) {
      throw new ApiError(400, "All required fields must be provided");
    }

    const pharma = await prisma.pharma.create({
      data: { name, address, city, state, pincode, contact },
    });

    res.status(201).json(new ApiResponse(201, pharma, "Pharma created successfully"));
  } catch (err) {
    next(err);
  }
};

// Get All Pharmas
export const getAllPharmas = async (req, res, next) => {
  try {
    const pharmas = await prisma.pharma.findMany({
      orderBy: { createdAt: "desc" },
      take: 50,
    });
    res.json(new ApiResponse(200, pharmas, "Pharmas fetched successfully"));
  } catch (err) {
    next(err);
  }
};

// Get Pharma by ID
export const getPharmaById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const pharma = await prisma.pharma.findUnique({ where: { id } });

    if (!pharma) throw new ApiError(404, "Pharma not found");

    res.json(new ApiResponse(200, pharma, "Pharma fetched successfully"));
  } catch (err) {
    next(err);
  }
};

// Update Pharma
export const updatePharma = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { name, address, city, state, pincode, contact } = req.body;

    const pharma = await prisma.pharma.update({
      where: { id },
      data: { name, address, city, state, pincode, contact },
    });

    res.json(new ApiResponse(200, pharma, "Pharma updated successfully"));
  } catch (err) {
    next(err);
  }
};

// Delete Pharma
export const deletePharma = async (req, res, next) => {
  try {
    const { id } = req.params;

    await prisma.pharma.delete({ where: { id } });

    res.json(new ApiResponse(200, null, "Pharma deleted successfully"));
  } catch (err) {
    next(err);
  }
};