# Phase 4 Test Data

This directory contains mock test data for end-to-end testing.

## Files

- `einvoice_sample_*.json` - Sample e-Invoice JSON payloads
- `test_commands.sh` - Curl commands for API testing
- `test_scenarios.json` - Complete test scenarios

## Usage

1. Start backend: `cd clarity-api && python -m uvicorn app.main:app --reload`
2. Get auth token: See test_commands.sh
3. Run test commands: `export TOKEN='...' && bash test_commands.sh`
