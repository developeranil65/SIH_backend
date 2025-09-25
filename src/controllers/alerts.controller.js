import { prisma } from "../utils/prisma.js";
import { ApiResponse } from "../utils/ApiResponse.js";

let lastChecked = new Date();

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

// 🔄 polling new rows from AggregatedSummary
export const pollAggregatedSummaries = async (io) => {
  const newRows = await prisma.aggregatedSummary.findMany({
    where: { createdAt: { gte: lastChecked } },
    orderBy: { createdAt: "asc" },
  });

  newRows.forEach(row => {
    io.emit("new-summary", row);
  });

  lastChecked = new Date();
};
