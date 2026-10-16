const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser', fullyParallel: false,
  use: { baseURL: 'http://127.0.0.1:8766', viewport: { width: 1440, height: 1000 } },
  webServer: { command: 'python studio.py --port 8766', url: 'http://127.0.0.1:8766', reuseExistingServer: !process.env.CI },
});
