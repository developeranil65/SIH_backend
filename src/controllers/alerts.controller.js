import { prisma } from "../utils/prisma.js";
import { ApiResponse } from "../utils/ApiResponse.js";
import { ApiError } from "../utils/ApiError.js";

export const getAlerts = async (req, res, next) => {
  try {
    const threshold = parseFloat(req.query.threshold || 0.7);

    const alerts = await prisma.aggregatedSummary.findMany({
      where: { outbreakRiskScore: { gte: threshold } },
      orderBy: { outbreakRiskScore: "desc" },
      take: 50,
    });

    res.json(new ApiResponse(200, alerts, `Alerts above threshold ${threshold}`));
  } catch (err) {
    next(err);
  }
};
