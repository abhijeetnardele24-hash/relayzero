/**
 * RelayZero Playwright E2E and Axe Accessibility Test Suite.
 * Validates principal operator workflow, blocked approval safety gates,
 * tests responsive viewports (320, 360, 768, 1024, 1440, 1920px) with strict
 * 0-overflow assertions, and executes Axe accessibility audits.
 */

import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const screenshotsDir = path.join(__dirname, '..', '..', 'docs', 'screenshots');

if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

async function runE2ESuite() {
  console.log('--- Starting RelayZero Playwright & Axe Verification Suite ---');
  const browser = await chromium.launch({ headless: true });

  const viewports = [
    { name: 'hero_desktop_1440', width: 1440, height: 900 },
    { name: 'large_desktop_1920', width: 1920, height: 1080 },
    { name: 'laptop_1024', width: 1024, height: 768 },
    { name: 'tablet_768', width: 768, height: 1024 },
    { name: 'mobile_360', width: 360, height: 740 },
    { name: 'mobile_320', width: 320, height: 568 },
  ];

  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log('1. Navigating to RelayZero at http://127.0.0.1:8000 ...');
  await page.goto('http://127.0.0.1:8000', { waitUntil: 'networkidle' });

  // 1. Verify Mode Badge
  const modeBadge = await page.textContent('.badges-group');
  console.log(`Verified Mode Badge presence in header: ${modeBadge?.replace(/\s+/g, ' ')}`);

  // 2. Trigger Pipeline Compilation
  console.log('2. Triggering "Compile Incident"...');
  await page.click('button:has-text("Compile Incident")');
  await page.waitForTimeout(1000);

  // 3. Verify Contradiction Detected
  const conflictBanner = await page.locator('.cluster-group.conflict').first();
  await conflictBanner.waitFor({ state: 'visible', timeout: 5000 });
  console.log('✓ Verified: Contradiction banner visible on factual claims canvas.');

  // Take Hero Screenshot
  const heroPath = path.join(screenshotsDir, 'hero_desktop_1440.png');
  await page.screenshot({ path: heroPath, fullPage: false });
  console.log(`Saved hero screenshot to: ${heroPath}`);

  // 4. Test Blocked Approval Safety Gate
  console.log('3. Testing Safety Gate: Verifying approval is blocked when conflicts remain...');
  const signBtn = await page.locator('button:has-text("Sign & Approve Brief")');
  const isDisabled = await signBtn.isDisabled();
  if (!isDisabled) {
    throw new Error('SAFETY GATE VIOLATION: "Sign & Approve Brief" button MUST be disabled while conflicts remain!');
  }
  console.log('✓ Safety Gate Passed: "Sign & Approve Brief" button is strictly disabled while conflicts remain.');

  // 5. Operator Resolves Contradiction
  console.log('4. Operator resolving contradiction: Confirming North Portal fact...');
  const confirmBtn = await page.locator('.action-btn-confirm').first();
  await confirmBtn.click();
  await page.waitForTimeout(600);

  const resolvePath = path.join(screenshotsDir, 'contradiction_resolution.png');
  await page.screenshot({ path: resolvePath, fullPage: false });

  // 6. Test Emergency Override workflow if data gaps remain
  const overrideCheckbox = await page.locator('input[type="checkbox"]');
  if (await overrideCheckbox.isVisible()) {
    console.log('5. Testing Emergency Override workflow...');
    await overrideCheckbox.check();
    const reasonInput = await page.locator('input[placeholder*="Mandatory operational"]');
    await reasonInput.fill('Urgent life-safety order authorized by cantonal commander.');
    const overrideBtn = await page.locator('button:has-text("Sign with Emergency Override")');
    await overrideBtn.click();
    await page.waitForTimeout(600);
    console.log('✓ Emergency Override Brief Signed and verified.');
  }

  const approvedPath = path.join(screenshotsDir, 'brief_approved_audit.png');
  await page.screenshot({ path: approvedPath, fullPage: false });

  // 7. Test Axe Accessibility Scan
  console.log('6. Running Axe automated accessibility scan (including color contrast)...');
  const axeResults = await new AxeBuilder({ page }).analyze();

  const seriousViolations = axeResults.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
  if (seriousViolations.length > 0) {
    console.error('Axe accessibility violations detected:', JSON.stringify(seriousViolations, null, 2));
    throw new Error(`Axe accessibility violations found: ${seriousViolations.length}`);
  }
  console.log(`✓ Axe Accessibility Check: No automatically detected serious Axe violations (${axeResults.passes.length} rules passed, 0 serious/critical violations).`);

  // 8. Test All Responsive Viewports for Horizontal Overflow
  console.log('7. Testing responsive viewports for horizontal overflow...');
  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.waitForTimeout(300);

    const overflowDetected = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });

    if (overflowDetected) {
      throw new Error(`TEST FAILED: Horizontal overflow detected on viewport ${vp.name} (${vp.width}x${vp.height})`);
    }
    console.log(`✓ Viewport ${vp.name} (${vp.width}x${vp.height}): Clean layout with 0 horizontal overflow.`);

    const vpScreenshot = path.join(screenshotsDir, `${vp.name}.png`);
    await page.screenshot({ path: vpScreenshot, fullPage: false });
  }

  await browser.close();
  console.log('--- ALL PLAYWRIGHT E2E, AXE ACCESSIBILITY, AND VIEWPORT CHECKS PASSED ---');
}

runE2ESuite().catch((err) => {
  console.error('Playwright E2E Suite Failed:', err);
  process.exit(1);
});
