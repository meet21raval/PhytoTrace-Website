from __future__ import annotations

from pathlib import Path
import re
import time
import pandas as pd
import streamlit as st

from core import extract_imppat_plant, safe_filename, RDKIT_OK
from exports import clean_df, build_basic_excel, build_advanced_excel

BRAND = "PhytoTrace"
FULL_NAME = "Plant Phytochemical Database & Retrieval Platform"
TAGLINE = "Explore Plants. Discover Molecules."

st.set_page_config(
    page_title="PhytoTrace | Plant Phytochemical Database",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --green:#145c43; --deep:#103f32; --mint:#e9f5ed; --leaf:#4c936b; --ink:#18332a; --muted:#64756b; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(180deg,#f5faf6 0%,#ffffff 40%,#f7faf8 100%); color:var(--ink); }
.block-container { max-width:1320px; padding-top:1.6rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#f0f7f1; border-right:1px solid #dce9df; }
.hero { background:linear-gradient(120deg,#103f32 0%,#176447 60%,#4c936b 100%); color:white; border-radius:24px; padding:34px 36px; margin-bottom:24px; position:relative; overflow:hidden; }
.hero:after { content:'✳'; position:absolute; right:34px; top:-42px; font-size:190px; opacity:.08; }
.hero h1 { font-family:'Manrope',sans-serif; font-size:clamp(2.2rem,4vw,3.35rem); font-weight:800; margin:0; letter-spacing:-1.5px; color:#fff; }
.hero p { color:#e2f1e6; font-size:1.03rem; margin:.45rem 0 0; }
.hero .tagline { color:#fff; font-weight:700; margin-top:1rem; }
.kicker { text-transform:uppercase; letter-spacing:1.6px; font-size:.72rem; font-weight:700; color:#b9e2c7; margin-bottom:8px; }
.section-title { font-family:'Manrope',sans-serif; font-weight:800; font-size:1.35rem; margin:.2rem 0 .35rem; color:#153d2f; }
.subtle { color:#66776d; font-size:.93rem; }
.metric-card { background:white; border:1px solid #e0ebe3; border-radius:16px; padding:17px 18px; box-shadow:0 5px 18px rgba(16,63,50,.04); min-height:104px; }
.metric-label { color:#66776d; font-size:.82rem; font-weight:600; }
.metric-value { color:#164e39; font-family:'Manrope',sans-serif; font-size:1.7rem; font-weight:800; margin-top:5px; }
.info-card { background:#fff; border:1px solid #e0ebe3; border-radius:16px; padding:20px; height:100%; }
.info-card h3 { color:#164e39; font-size:1.02rem; margin:.25rem 0; }
.info-card p { color:#66776d; font-size:.9rem; margin:0; }
.badge { display:inline-block; background:#e3f2e7; color:#145c43; padding:5px 10px; border-radius:999px; font-size:.75rem; font-weight:700; }
.stButton>button[kind="primary"] { background:#176447; border-color:#176447; border-radius:10px; font-weight:700; min-height:46px; }
.stDownloadButton>button { border-radius:10px; font-weight:700; min-height:42px; }
hr { border-color:#e0ebe3; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)




with st.sidebar:
    st.markdown("## 🌿 PhytoTrace")
    st.caption("Plant Phytochemical Database")
    st.markdown("---")
    st.markdown("### Search settings")
    plant_name = st.text_input("Plant scientific name", value="Rheum palmatum", placeholder="e.g., Catharanthus roseus")
    st.info("Current website build uses the IMPPAT retrieval workflow. Additional database sources will be added only after their retrieval is validated.")
    st.markdown("---")
    st.markdown("**Data integrity**")
    st.caption("Missing values are left blank. Retrieved records and calculated molecular descriptors are kept distinguishable.")

st.markdown(f"""
<div class="hero">
  <div class="kicker">Plant science · Natural products · Molecular data</div>
  <h1>🌿 {BRAND}</h1>
  <p>{FULL_NAME}</p>
  <p class="tagline">{TAGLINE}</p>
</div>
""", unsafe_allow_html=True)

c1,c2,c3 = st.columns(3)
with c1:
    st.markdown('<div class="info-card"><span class="badge">01 · Search</span><h3>Start with a plant</h3><p>Enter a scientific name to retrieve available phytochemical records.</p></div>',unsafe_allow_html=True)
with c2:
    st.markdown('<div class="info-card"><span class="badge">02 · Explore</span><h3>Review compound data</h3><p>Inspect identifiers, structures, classifications, and calculated descriptors where available.</p></div>',unsafe_allow_html=True)
with c3:
    st.markdown('<div class="info-card"><span class="badge">03 · Export</span><h3>Download research tables</h3><p>Choose a basic workbook or a detailed multi-sheet molecular-data report.</p></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)
st.markdown('<div class="section-title">Plant phytochemical search</div>',unsafe_allow_html=True)
st.markdown('<div class="subtle">Search the IMPPAT plant record and build a downloadable report. Retrieval time depends on the source website and number of compound records.</div>',unsafe_allow_html=True)

left, right = st.columns([4,1])
with left:
    st.write(f"**Plant to search:** `{plant_name.strip() or 'Not entered'}`")
with right:
    run_search = st.button("Retrieve phytochemicals", type="primary", use_container_width=True)

if "phyto_df" not in st.session_state:
    st.session_state.phyto_df = None
    st.session_state.phyto_plant = ""
    st.session_state.phyto_logs = []

if run_search:
    if not plant_name.strip():
        st.error("Enter a plant scientific name first.")
    else:
        logs=[]
        progress=st.progress(0, text="Connecting to IMPPAT…")
        try:
            with st.spinner(f"Retrieving records for {plant_name.strip()}… this may take a few minutes."):
                df=extract_imppat_plant(plant_name.strip(),log=lambda msg: logs.append(str(msg)))
            st.session_state.phyto_df = df
            st.session_state.phyto_plant = plant_name.strip()
            st.session_state.phyto_logs = logs
            progress.progress(100,text="Retrieval finished")
        except Exception as exc:
            st.session_state.phyto_df = None
            st.session_state.phyto_logs = logs + [f"ERROR: {type(exc).__name__}: {exc}"]
            st.error("Retrieval did not complete. The source website may be unavailable or its page structure may have changed.")
            st.exception(exc)
        finally:
            time.sleep(.3)
            progress.empty()

if st.session_state.phyto_logs:
    with st.expander("Retrieval log", expanded=st.session_state.phyto_df is None):
        st.code("\n".join(st.session_state.phyto_logs[-100:]) or "No log messages.")

result = st.session_state.phyto_df
if result is not None:
    df=clean_df(result)
    plant=st.session_state.phyto_plant
    st.markdown("---")
    st.markdown('<div class="section-title">Retrieval summary</div>',unsafe_allow_html=True)
    unique=int(df["IMPPAT_ID"].nunique()) if "IMPPAT_ID" in df else len(df)
    with_smiles=int(df["SMILES"].astype(str).str.strip().ne("").sum()) if "SMILES" in df else 0
    valid=int(df["RDKit_valid_structure"].astype(str).eq("Yes").sum()) if "RDKit_valid_structure" in df else 0
    metrics=st.columns(4)
    for col,label,value in zip(metrics,["Association rows","Unique IMPPAT IDs","Records with SMILES","Valid RDKit structures"],[len(df),unique,with_smiles,valid]):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value:,}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown('<div class="section-title">Compound records</div>',unsafe_allow_html=True)
    searchable = df.copy()
    search_filter=st.text_input("Filter visible results",placeholder="Search compound name, ID, plant part, or synonym")
    if search_filter.strip():
        mask=searchable.astype(str).apply(lambda col: col.str.contains(re.escape(search_filter.strip()),case=False,na=False)).any(axis=1)
        searchable=searchable[mask]
    preferred=["Plant_part","Phytochemical_name","IMPPAT_ID","Synonyms","Molecular_formula","MW_g_mol","SMILES","ClassyFire_Class","NPClassifier_Class"]
    visible_cols=[c for c in preferred if c in searchable.columns]
    if not visible_cols:
        visible_cols=list(searchable.columns[:10])
    st.dataframe(searchable[visible_cols],use_container_width=True,hide_index=True,height=430)
    st.caption(f"Showing {len(searchable):,} of {len(df):,} records. Empty fields mean information was not available in the retrieved record or could not be calculated.")

    st.markdown("---")
    st.markdown('<div class="section-title">Download Excel reports</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtle">Both workbooks use the same retrieval results. The advanced workbook separates compound, descriptor, classification, source, and summary tables.</div>',unsafe_allow_html=True)
    b1,b2=st.columns(2)
    try:
        basic_bytes=build_basic_excel(df,plant)
        advanced_bytes=build_advanced_excel(df,plant)
        with b1:
            st.markdown("#### Basic Excel")
            st.caption("Essential compound identifiers and chemical structure fields.")
            st.download_button("Download Basic Excel",data=basic_bytes,file_name=f"{safe_filename(plant)}_PhytoTrace_Basic.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        with b2:
            st.markdown("#### Advanced Excel")
            st.caption("Multiple worksheets with descriptors, classifications, identifiers, and summary.")
            st.download_button("Download Advanced Excel",data=advanced_bytes,file_name=f"{safe_filename(plant)}_PhytoTrace_Advanced.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    except Exception as exc:
        st.error(f"Could not prepare Excel reports: {exc}")

st.markdown("---")
st.markdown('<div class="subtle">PhytoTrace is a research-support tool. Database records and computed descriptors should be checked against their cited sources before scientific publication. Molecular descriptors are calculated from available SMILES; they do not establish biological activity.</div>',unsafe_allow_html=True)
