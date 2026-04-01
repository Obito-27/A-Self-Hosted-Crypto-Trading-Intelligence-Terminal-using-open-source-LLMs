const pptxgen = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

// Path to the html2pptx.js script from the skill
const html2pptxPath = 'C:\\Users\\ASUS\\AppData\\Roaming\\npm\\node_modules\\@google\\gemini-cli\\skills\\pptx\\scripts\\html2pptx.js';
// Fallback if global path is wrong
const localHtml2pptx = 'C:\\Users\\ASUS\\.gemini\\skills\\pptx\\scripts\\html2pptx.js';
const html2pptx = require(fs.existsSync(localHtml2pptx) ? localHtml2pptx : html2pptxPath);

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Gemini AI';
    pptx.title = 'CryptoTerminal AI Hackathon Presentation';

    console.log("Starting presentation v2 creation...");

    for (let i = 1; i <= 12; i++) {
        const slidePath = path.join(__dirname, 'presentation_v2', `slide${i}.html`);
        if (fs.existsSync(slidePath)) {
            console.log(`Processing slide ${i}...`);
            try {
                await html2pptx(slidePath, pptx);
            } catch (err) {
                console.error(`Error on slide ${i}:`, err);
            }
        }
    }

    const outputFile = 'CryptoTerminal_Full_Explanation.pptx';
    await pptx.writeFile({ fileName: outputFile });
    console.log(`Presentation saved as ${outputFile}`);
}

createPresentation().catch(err => {
    console.error("Fatal error:", err);
    process.exit(1);
});
