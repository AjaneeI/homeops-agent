const { test, expect } = require("@playwright/test");

const viewports = [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
];

const scenarios = [
  {
    id: "all-clear",
    summary: "Good Night Check complete.",
    safeActions: "0 safe actions",
    humanReview: "None",
    core: "Clear",
    actionText: "No automatic actions needed.",
  },
  {
    id: "fix-needed",
    summary: "Good Night Check complete.",
    safeActions: "3 safe actions",
    humanReview: "None",
    core: "Clear",
    actionText: "Dimmed bedside bulb to 20%",
  },
  {
    id: "lock-unknown",
    summary: "Good Night Check complete with human review required.",
    safeActions: "1 safe action",
    humanReview: "1 needed",
    core: "Review",
    approvalText: "Verify front door lock",
  },
  {
    id: "device-failure",
    summary: "Good Night Check complete.",
    safeActions: "1 safe action",
    humanReview: "None",
    core: "Degraded",
    actionText: "Device API is unavailable.",
    auditText: "safe action failed",
  },
];

for (const viewport of viewports) {
  for (const scenario of scenarios) {
    test(`${scenario.id} preserves scenario semantics at ${viewport.name} width`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto("http://127.0.0.1:4173");

      await page.selectOption("#scenario", scenario.id);
      await page.getByRole("button", { name: "Run Good Night Check" }).click();

      await expect(page.locator("#summary")).toHaveText(scenario.summary);
      await expect(page.locator("#devices-checked")).toHaveText("5 devices");
      await expect(page.locator("#safe-actions")).toHaveText(scenario.safeActions);
      await expect(page.locator("#human-review")).toHaveText(scenario.humanReview);
      await expect(page.locator(".agent-core strong")).toHaveText(scenario.core);

      if (scenario.actionText) {
        await expect(page.locator("#actions")).toContainText(scenario.actionText);
      }
      if (scenario.approvalText) {
        await expect(page.locator("#approvals")).toContainText(scenario.approvalText);
      }
      if (scenario.auditText) {
        await expect(page.locator("#audit")).toContainText(scenario.auditText);
      }

      if (scenario.id === "lock-unknown") {
        const traceItems = await page.locator("#trace .trace-item").allTextContents();
        const automaticLockActions = traceItems.filter(
          (item) => item.startsWith("execute_safe_action") && item.includes("front-door")
        );
        expect(automaticLockActions).toHaveLength(0);
      }

      const hasHorizontalOverflow = await page.evaluate(
        () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
      );
      expect(hasHorizontalOverflow).toBe(false);
    });
  }
}
