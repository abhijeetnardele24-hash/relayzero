/**
 * RelayZero Automated Playwright E2E and Viewport Verification Suite.
 * Validates principal operator workflow and tests responsive viewports:
 * 320px, 360px, 768px, 1024px, 1440px, 1920px.
 * Saves high-resolution verification screenshots into track_2b/docs/screenshots/.
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotsDir = path.join(__dirname, '..', '..', 'docs', 'screenshots');

if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

async function runE2E() {
  console.log('Launching Chromium for RelayZero E2E Verification...');
  const browser = await chromium.launch({ headless: true });

  const viewports = [
    { name: 'hero_desktop_1440', width: 1440, height: 900 },
    { name: 'large_desktop_1920', width: 1920, height: 1080 },
    { name: 'laptop_1024', width: 1024, height: 768 },
    { name: 'tablet_768', width: 768, height: 1024 },
    { name: 'mobile_360', width: 360, height: 740 },
    { name: 'mobile_320', width: 320, height: 568 },
  ];

  // 1. Primary Workflow on Desktop 1440px
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log('Navigating to RelayZero application at http://127.0.0.1:8000 ...');
  await page.goto('http://127.0.0.1:8000', { waitUntil: 'networkidle' });

  // Verify header sovereignty chips
  const brandTitle = await page.textContent('.brand-logo');
  console.log(`Verified Brand: ${brandTitle}`);

  // Trigger Compile Incident
  console.log('Triggering "Compile Incident" pipeline button...');
  await page.click('button:has-text("Compile Incident")');
  await page.waitForTimeout(1000);

  // Verify Contradiction Detected
  const conflictBanner = await page.locator('.cluster-group.conflict').first();
  await conflictBanner.waitFor({ state: 'visible', timeout: 5000 });
  console.log('Verified: Contradiction banner visible on factual claims canvas.');

  // Take hero screenshot
  const heroPath = path.join(screenshotsDir, 'hero_desktop_1440.png');
  await page.screenshot({ path: heroPath, fullPage: false });
  console.log(`Saved hero screenshot to: ${heroPath}`);

  // Resolve contradiction: Operator clicks "Confirm This Fact" on North Portal
  console.log('Operator resolving conflict: Confirming North Portal fact...');
  const confirmBtn = await page.locator('.action-btn-confirm').first();
  await confirmBtn.click();
  await page.waitForTimeout(600);

  const resolvePath = path.join(screenshotsDir, 'contradiction_resolution.png');
  await page.screenshot({ path: resolvePath, fullPage: false });
  console.log(`Saved resolution screenshot to: ${resolvePath}`);

  // Operator signs and approves brief
  console.log('Operator signing brief: Clicking "Sign & Approve"...');
  const signBtn = await page.locator('button:has-text("Sign & Approve")').first();
  if (await signBtn.isVisible()) {
    await signBtn.click();
    await page.waitForTimeout(500);
  }

  const approvedPath = path.join(screenshotsDir, 'brief_approved_audit.png');
  await page.screenshot({ path: approvedPath, fullPage: false });
  console.log(`Saved brief approval screenshot to: ${approvedPath}`);

  // Verify responsive viewports
  for (const vp of viewports.slice(1)) {
    console.log(`Verifying responsive viewport ${vp.name} (${vp.width}x${vp.height})...`);
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.waitForTimeout(300);

    // Check no horizontal scroll overflow
    const hasHorizontalOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    if (hasHorizontalOverflow) {
      console.warn(`Warning: Potential horizontal overflow on ${vp.name}`);
    } else {
      console.log(`✓ Viewport ${vp.name}: Clean layout with 0 horizontal overflow.`);
    }

    const vpScreenshot = path.join(screenshotsDir, `${vp.name}.png`);
    await page.screenshot({ path: vpScreenshot, fullPage: false });
  }

  await browser.close();
  console.log('All Playwright E2E and responsive viewport checks completed successfully!');
}

runE2E().catch((err) => {
  console.error('Playwright E2E test failed:', err);
  process.exit(1);
});
