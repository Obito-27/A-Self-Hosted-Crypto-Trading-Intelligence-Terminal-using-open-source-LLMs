const pptxgen = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

// Path to the html2pptx.js script from the skill
const html2pptxPath = 'C:\\Users\\ASUS\\.gemini\\skills\\pptx\\scripts\\html2pptx.js';
const html2pptx = require(html2pptxPath);

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Gemini AI';
    pptx.title = 'CryptoTerminal AI Hackathon Presentation';

    console.log("Starting presentation creation...");

    for (let i = 1; i <= 12; i++) {
        const slidePath = path.join(__dirname, 'presentation_slides', `slide${i}.html`);
        if (fs.existsSync(slidePath)) {
            console.log(`Processing slide ${i}...`);
            try {
                await html2pptx(slidePath, pptx);
            } catch (err) {
                console.error(`Error on slide ${i}:`, err);
            }
        } else {
            console.warn(`Slide ${i} not found at ${slidePath}`);
        }
    }

    const outputFile = 'CryptoTerminal_AI_Presentation.pptx';
    await pptx.writeFile({ fileName: outputFile });
    console.log(`Presentation saved as ${outputFile}`);
}

createPresentation().catch(err => {
    console.error("Fatal error creating presentation:", err);
    process.exit(1);
});
