import express from "express"; // Importing express using ES module syntax
import fs from "fs"; // Importing fs
import path from "path"; // Importing path
import cors from "cors"; // Importing cors

const app = express();
const PORT = 5000;

app.use(cors());

// Define absolute paths for external directories
const IMAGES_DIR = 'C:/Users/Happy yadav/Desktop/aura.ai/hackcbs-backend/images';  // Replace with your absolute path
const SUMMARY_FILE_PATH = 'C:/Users/Happy yadav/Desktop/aura.ai/hackcbs-backend/llm_prompt.txt';  // Replace with your absolute path

// Serve images as static files
app.use('/images', express.static(IMAGES_DIR)); // This allows the images to be accessed through http://localhost:5000/images/

// Route to fetch images
app.get('/api/images', (req, res) => {
    fs.readdir(IMAGES_DIR, (err, files) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to fetch images' });
        }
        const imageFiles = files.filter(file => /\.(jpg|jpeg|png|gif)$/i.test(file));
        // Send just the filenames of the images instead of the absolute paths
        res.json({ images: imageFiles });
    });
});

// Route to fetch summary text
app.get('/api/summary', (req, res) => {
    fs.readFile(SUMMARY_FILE_PATH, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to read summary file' });
        }
        res.json({ summary: data });
    });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
