# Multimodal Construction Intelligence Platform

Skill Wallet Capstone Project 1 — a Streamlit application for construction-site decision support.

## Features
- Site Safety & PPE Audit with image upload, Gemini vision analysis (optional), hazard list, and JSON export.
- Crack Diagnostics with image upload, cautious preliminary triage, and JSON export.
- Planning & Real Estate Valuation with editable INR estimates, progress, and indicative material quantities.
- Weather-aware site advisory and construction Q&A assistant.
- Demonstration mode works without an API key.

## Run locally
1. Install Python 3.10 or newer.
2. Extract this folder and open a terminal in it.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   streamlit run app.py
   ```

## Gemini API key
The app accepts an API key in the sidebar for the current session. Alternatively set `GEMINI_API_KEY` in your environment. Never commit secrets to GitHub. If no key is supplied, demo mode is available and is clearly labelled.

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Go to https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy, wait for the app to start, then test each tab.
5. Copy the HTTPS app URL and submit it in Skill Wallet's **Add Demo Link** field.

## Safety and limitations
This is a capstone decision-support demo, not a certified safety inspection or structural engineering tool. Image-only crack width estimates are unreliable without a scale. All planning costs and material quantities are illustrative assumptions and must be verified using local rates, drawings, and qualified professionals.
