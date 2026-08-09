/**
 * Fathom AI — Frontend Configuration
 * ============================================================================
 * Update this file when deploying to a new environment.
 * DO NOT commit API keys here — those belong in Worker environment variables.
 */

const FATHOM_CONFIG = {
  // Primary worker endpoint — Tencent Cloud SCF (domestic)
  workerUrl: 'https://1458338296-html16eshd.ap-guangzhou.tencentscf.com/',

  // App metadata
  appName: 'Fathom / 知彼',
  version: '5.8.0',

  // Feature flags
  features: {
    simulate: true,    // Simulated negotiation mode
    compare: true,     // Country comparison mode
  }
};
