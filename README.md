# PhytoTrace Website V1

**Brand:** PhytoTrace  
**Full name:** PhytoTrace — Plant Phytochemical Database & Retrieval Platform  
**Website title:** PhytoTrace | Plant Phytochemical Database  
**Tagline:** Explore Plants. Discover Molecules.

## What's in this first website build
- Responsive Streamlit web interface
- IMPPAT plant phytochemical retrieval using the project's existing retrieval functions
- Result summary and searchable compound table
- Basic Excel export and Advanced multi-sheet Excel export
- RDKit descriptors calculated from retrieved SMILES when RDKit is available
- Retrieval log and transparent handling of missing fields

## Run locally on Windows
1. Install Python 3.11 or 3.12 (64-bit) if it is not already installed.
2. Extract this folder.
3. Open Command Prompt in this folder.
4. Run:
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   streamlit run app.py
   ```
5. The browser should open automatically. If it does not, open the local URL printed in Command Prompt (usually `http://localhost:8501`).

## Deploying online
This folder is structured for a Streamlit-compatible host. Push these files to a separate GitHub repository or a new branch, then connect that repository to the host and set `app.py` as the entry point. Keep any existing desktop app and its repository unchanged until the web version is validated.

## Important limitations
- The first web build enables IMPPAT retrieval only. NPASS is not enabled in this web interface because the existing NPASS retrieval path has shown unreliable/empty results and should be repaired and tested before exposing it as a working source.
- Live source retrieval depends on the IMPPAT website being reachable and its page structure remaining compatible with the parser. This build has not yet been live-tested against the external database.
- The app does not invent missing values. RDKit descriptors are computed values, not source-database measurements or evidence of biological activity.
- This is a web application, not a static HTML website; hosting is required to make it publicly accessible.

## Google Search visibility (after publishing)
1. Publish the app to a public URL first; Google cannot index a local `localhost` address.
2. Create a Google Search Console property for the public URL and verify ownership using a method supported by your hosting setup.
3. Use the exact page title `PhytoTrace | Plant Phytochemical Database` and the tagline `Explore Plants. Discover Molecules.` consistently in public-facing descriptions.
4. Request indexing for the public URL in Search Console and monitor the indexing report. Discovery and ranking can take time and are not guaranteed.
5. Note: Streamlit is optimized for interactive data apps and offers less direct SEO control than a conventional server-rendered website. If strong Google search visibility becomes a priority, the next phase should add an SEO-friendly public landing page and metadata while retaining this retrieval app.
