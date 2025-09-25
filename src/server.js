import dotenv from "dotenv";
dotenv.config({ path: "./.env" });
import { app } from "./app.js";

import { createServer } from "http";
import { Server } from "socket.io";

const server = createServer(app);

const io = new Server(server, {
  cors: {
    origin: process.env.CORS_ORIGIN || "*",
    methods: ["GET", "POST"]
  }
});

// Socket.io connection
io.on("connection", (socket) => {
  console.log("New client connected:", socket.id);

  socket.on("disconnect", () => {
    console.log("Client disconnected:", socket.id);
  });
});

// Export io for other modules (controllers)
export { io };

app.listen(process.env.PORT, ()=>{
    console.log(`App is listening on ${process.env.PORT}`);
});


/* ---------------- NEW PART: Poll AggregatedSummary ---------------- */
import { prisma } from "./utils/prisma.js";

let lastChecked = new Date();

async function pollAggregatedSummaries() {
  try {
    const newRows = await prisma.aggregatedSummary.findMany({
      where: { createdAt: { gte: lastChecked } },
      orderBy: { createdAt: "asc" },
    });

    newRows.forEach(row => {
      io.emit("new-summary", row); // 🔥 push to all connected clients
    });

    lastChecked = new Date();
  } catch (err) {
    console.error("Polling error:", err);
  }
}

// run every 5s
setInterval(pollAggregatedSummaries, 50000);
