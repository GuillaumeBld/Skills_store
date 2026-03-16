#!/usr/bin/env node

/**
 * NotebookLM Watermark Remover
 * Removes watermarks from NotebookLM-generated PDF slide decks.
 * Algorithm extracted from SlideClean (texture cloning + edge feathering).
 *
 * Usage:
 *   node clean-watermark.js <input.pdf> [output.pdf]
 *   node clean-watermark.js --batch <directory>
 */

import fs from 'fs';
import path from 'path';
import { createCanvas } from 'canvas';
import { PDFDocument } from 'pdf-lib';
import pdfjsLib from 'pdfjs-dist/legacy/build/pdf.js';

const { getDocument } = pdfjsLib;

// Watermark region configuration (NotebookLM fixed position: bottom-right)
const WM_CONFIG = {
  widthRatio: 0.0825,        // 8.25% of image width
  heightRatio: 0.0375,       // 3.75% of image height
  marginRightRatio: 0.0025,  // 0.25% right margin
  marginBottomRatio: 0.0027, // 0.27% bottom margin
  featherSize: 12            // Edge feathering gradient in pixels
};

/**
 * Remove watermark from a canvas context using texture cloning + edge feathering.
 * Clones pixels from the region directly above the watermark and blends edges.
 */
function removeWatermark(ctx, w, h) {
  const wmW = Math.round(w * WM_CONFIG.widthRatio);
  const wmH = Math.round(h * WM_CONFIG.heightRatio);
  const mr = Math.round(w * WM_CONFIG.marginRightRatio);
  const mb = Math.round(h * WM_CONFIG.marginBottomRatio);

  const x = w - wmW - mr;
  const y = h - wmH - mb;
  const srcY = Math.max(0, y - wmH);

  if (srcY < 0) {
    console.error(`WARN: watermark too close to top edge, skipping`);
    return;
  }

  const src = ctx.getImageData(x, srcY, wmW, wmH);
  const dst = ctx.getImageData(x, y, wmW, wmH);
  const res = ctx.createImageData(wmW, wmH);

  for (let i = 0; i < wmH; i++) {
    for (let j = 0; j < wmW; j++) {
      const idx = (i * wmW + j) * 4;
      let alpha = 1.0;
      if (i < WM_CONFIG.featherSize) alpha = Math.min(alpha, i / WM_CONFIG.featherSize);
      if (j < WM_CONFIG.featherSize) alpha = Math.min(alpha, j / WM_CONFIG.featherSize);

      for (let c = 0; c < 4; c++) {
        res.data[idx + c] = Math.round(
          dst.data[idx + c] * (1 - alpha) + src.data[idx + c] * alpha
        );
      }
    }
  }

  ctx.putImageData(res, x, y);
}

/**
 * Render a PDF page to canvas, remove watermark, return PNG buffer.
 */
async function processPage(page, scale = 2) {
  const viewport = page.getViewport({ scale });
  const canvas = createCanvas(viewport.width, viewport.height);
  const ctx = canvas.getContext('2d');

  await page.render({ canvasContext: ctx, viewport }).promise;
  removeWatermark(ctx, canvas.width, canvas.height);

  return canvas.toBuffer('image/png');
}

/**
 * Process a full PDF: render each page, remove watermarks, save new PDF.
 * @param {string} inputPath - Input PDF path
 * @param {string} [outputPath] - Output PDF path (default: {name}_cleaned.pdf)
 * @returns {Promise<string>} Output file path
 */
async function cleanPDF(inputPath, outputPath) {
  if (!fs.existsSync(inputPath)) {
    throw new Error(`File not found: ${inputPath}`);
  }
  if (path.extname(inputPath).toLowerCase() !== '.pdf') {
    throw new Error(`Not a PDF file: ${inputPath}`);
  }

  if (!outputPath) {
    const dir = path.dirname(inputPath);
    const basename = path.basename(inputPath, '.pdf');
    outputPath = path.join(dir, `${basename}_cleaned.pdf`);
  }

  const data = new Uint8Array(fs.readFileSync(inputPath));
  const pdfDoc = await getDocument({ data, useWorkerFetch: false, isEvalSupported: false }).promise;
  const totalPages = pdfDoc.numPages;

  console.log(`Processing ${path.basename(inputPath)} (${totalPages} pages)`);

  const newPdf = await PDFDocument.create();

  for (let i = 1; i <= totalPages; i++) {
    process.stdout.write(`  page ${i}/${totalPages}\r`);
    const page = await pdfDoc.getPage(i);
    const imageBuffer = await processPage(page);

    const pngImage = await newPdf.embedPng(imageBuffer);
    const viewport = page.getViewport({ scale: 2 });
    const pdfPage = newPdf.addPage([viewport.width, viewport.height]);
    pdfPage.drawImage(pngImage, { x: 0, y: 0, width: viewport.width, height: viewport.height });
  }

  const pdfBytes = await newPdf.save();
  fs.writeFileSync(outputPath, pdfBytes);

  const inSize = (fs.statSync(inputPath).size / 1024 / 1024).toFixed(2);
  const outSize = (pdfBytes.length / 1024 / 1024).toFixed(2);
  console.log(`  done: ${inSize}MB -> ${outSize}MB => ${path.basename(outputPath)}`);

  return outputPath;
}

// --- CLI ---

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`Usage:
  node clean-watermark.js <input.pdf> [output.pdf]
  node clean-watermark.js --batch <directory>`);
    process.exit(0);
  }

  try {
    if (args[0] === '--batch') {
      const dir = args[1];
      if (!dir || !fs.existsSync(dir)) {
        console.error(`ERROR: directory not found: ${dir}`);
        process.exit(1);
      }
      const pdfs = fs.readdirSync(dir)
        .filter(f => f.toLowerCase().endsWith('.pdf') && !f.includes('_cleaned'))
        .map(f => path.join(dir, f));

      if (pdfs.length === 0) {
        console.log('No PDF files found in directory');
        process.exit(0);
      }

      console.log(`Batch: ${pdfs.length} PDF(s) in ${dir}`);
      for (const pdf of pdfs) {
        await cleanPDF(pdf);
      }
      console.log(`Batch complete: ${pdfs.length} file(s) cleaned`);
    } else {
      const inputPath = path.resolve(args[0]);
      const outputPath = args[1] ? path.resolve(args[1]) : undefined;
      await cleanPDF(inputPath, outputPath);
    }
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(1);
  }
}

main();
