# Troubleshooting - Document AI Returns 0 Pages

## Issue: Processor Returns Empty Results (0 pages, 0 text)

**Symptoms:** API accepts requests, quotas show usage, but `document.pages = 0` and `document.text = ""`

**Root Cause:** Google Cloud billing account is **under review/verification** - API calls are accepted but document processing is silently blocked until billing is verified.

**Solution:** Wait 24-48 hours for Google Cloud billing verification to complete. Check email for verification requests (identity verification, payment confirmation). Once verified, processing will work immediately.

**Quick Check:** Go to https://console.cloud.google.com/billing - if status shows "Under Review" or yellow warning, that's the issue.

**Workaround:** Use a different Google Cloud project with already-verified billing, or contact Google Cloud Support to expedite verification.

---

**Date:** Nov 30, 2025  
**Project:** vudr0311  
**Processor:** 91f4e596a0b1c39d (Layout Parser - working correctly once billing verified)

