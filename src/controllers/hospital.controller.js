import { prisma } from "../utils/prisma.js";
import { ApiError } from "../utils/ApiError.js";
import { ApiResponse } from "../utils/ApiResponse.js";
import { asyncHandler } from "../utils/asyncHandler.js";

export const getHospitals = asyncHandler(async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit || "50", 10), 200);
  const page = Math.max(parseInt(req.query.page || "1", 10), 1);
  const district = req.query.district;

  const where = district ? { district } : {};

  const hospitals = await prisma.hospitalRecord.findMany({
    where,
    orderBy: { visitDate: "desc" },
    take: limit,
    skip: (page - 1) * limit,
  });

  return res
    .status(200)
    .json(new ApiResponse(200, hospitals, "Hospital records fetched"));
});

export const getHospitalById = asyncHandler(async (req, res) => {
  const { id } = req.params;

  const hospital = await prisma.hospitalRecord.findUnique({
    where: { id: Number(id) },
  });

  if (!hospital) {
    throw new ApiError(404, "Hospital record not found");
  }

  return res
    .status(200)
    .json(new ApiResponse(200, hospital, "Hospital record fetched"));
});
