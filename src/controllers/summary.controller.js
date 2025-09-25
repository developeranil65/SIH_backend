import { prisma } from "../utils/prisma.js";
import { ApiError } from "../utils/ApiError.js";
import { ApiResponse } from "../utils/ApiResponse.js";

// Get latest aggregated data for all districts
export const getLatestSummary = async (req, res, next) => {
  try {
    // For each district → latest date entry
    const summaries = await prisma.$queryRaw`
      SELECT DISTINCT ON ("district") *
      FROM "AggregatedSummary"
      ORDER BY "district", "date" DESC
    `;

    res.json(new ApiResponse(200, summaries, "Latest summary per district fetched"));
  } catch (err) {
    next(err);
  }
};

// Get time-series for a district
export const getDistrictTrend = async (req, res, next) => {
  try {
    const { district } = req.params;

    if (!district) throw new ApiError(400, "District is required");

    const trend = await prisma.aggregatedSummary.findMany({
      where: { district },
      orderBy: { date: "asc" },
      take: 30, // last 30 days
    });

    res.json(new ApiResponse(200, trend, `Trend data for ${district}`));
  } catch (err) {
    next(err);
  }
};

// Admin/debug: get all summaries (paginated)
export const getAllSummaries = async (req, res, next) => {
  try {
    const limit = parseInt(req.query.limit || 50);
    const summaries = await prisma.aggregatedSummary.findMany({
      orderBy: { date: "desc" },
      take: limit,
    });

    res.json(new ApiResponse(200, summaries, "Summaries fetched"));
  } catch (err) {
    next(err);
  }
};
