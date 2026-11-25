
require("dotenv").config();

const express = require("express");
const { MongoClient } = require("mongodb");
const os = require("os");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve frontend files
app.use(express.static(path.join(__dirname, "public")));

// MongoDB configuration
const MONGO_URL = process.env.MONGO_URL;

if (!MONGO_URL) {
    throw new Error("MONGO_URL environment variable is missing");
}

const client = new MongoClient(MONGO_URL);

let calculations;

// Get the IP address of this application container/pod
function getPodIP() {
    const interfaces = os.networkInterfaces();

    for (const name of Object.keys(interfaces)) {
        for (const address of interfaces[name]) {
            if (address.family === "IPv4" && !address.internal) {
                return address.address;
            }
        }
    }

    return "127.0.0.1";
}

// Get pod name from HOSTNAME environment variable
function getPodName() {
    return process.env.HOSTNAME || os.hostname();
}

// Helper function to round values to 2 decimal places
function round(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

// POST /api/emi
app.post("/api/emi", async (req, res) => {
    try {
        const { P, rate, n } = req.body;

        // Validate inputs
        if (
            P === undefined || rate === undefined || n === undefined ||
            P === "" || rate === "" || n === ""
        ) {
            return res.status(400).json({
                error: "All three inputs are required."
            });
        }

        const principal = Number(P);
        const annualRate = Number(rate);
        const months = Number(n);

        if (
            !Number.isFinite(principal) ||
            !Number.isFinite(annualRate) ||
            !Number.isInteger(months) ||
            principal <= 0 ||
            annualRate <= 0 ||
            months <= 0
        ) {
            return res.status(400).json({
                error: "Loan amount, interest rate and tenure must be positive numbers. Tenure must be a whole number."
            });
        }

        // Convert annual interest rate to monthly rate
        const r = annualRate / 12 / 100;

        // Calculate EMI
        const power = Math.pow(1 + r, months);

        const emi = principal * r * power / (power - 1);

        const totalPayment = emi * months;
        const totalInterest = totalPayment - principal;

        // Identify the application pod
        const servedBy = getPodName();
        const podIP = getPodIP();

        // Create MongoDB document
        const record = {
            principal,
            rate: annualRate,
            months,
            emi: round(emi),
            servedBy,
            createdAt: new Date()
        };

        // Save calculation in MongoDB
        const result = await calculations.insertOne(record);

        // Send JSON response
        res.json({
            emi: round(emi),
            totalPayment: round(totalPayment),
            totalInterest: round(totalInterest),
            servedBy,
            podIP,
            id: result.insertedId
        });

    } catch (error) {
        console.error("EMI calculation error:", error);

        res.status(500).json({
            error: "Unable to calculate EMI or save the result."
        });
    }
});

// GET /api/history
app.get("/api/history", async (req, res) => {
    try {
        const history = await calculations
            .find({})
            .sort({ createdAt: -1 })
            .limit(10)
            .toArray();

        res.json(history);

    } catch (error) {
        console.error("History error:", error);

        res.status(500).json({
            error: "Unable to retrieve calculation history."
        });
    }
});

// GET /health
app.get("/health", async (req, res) => {
    try {
        await client.db().command({ ping: 1 });

        res.status(200).json({
            status: "healthy",
            mongodb: "connected"
        });

    } catch (error) {
        res.status(503).json({
            status: "unhealthy",
            mongodb: "disconnected"
        });
    }
});

// Connect to MongoDB and start server
async function startServer() {
    try {
        await client.connect();

        const db = client.db("emidb");
        calculations = db.collection("calculations");

        console.log("Connected to MongoDB successfully!");
        console.log("Database: emidb");
        console.log("Collection: calculations");

        app.listen(PORT, "0.0.0.0", () => {
            console.log(`Server running on port ${PORT}`);
            console.log(`Pod name: ${getPodName()}`);
            console.log(`Pod IP: ${getPodIP()}`);
        });

    } catch (error) {
        console.error("Failed to start application:", error);
        process.exit(1);
    }
}

startServer();
