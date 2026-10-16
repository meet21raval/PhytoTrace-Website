from __future__ import annotations

from io import BytesIO
import pandas as pd

from core import RDKIT_OK

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else x)
    return out


def pick_columns(df: pd.DataFrame, preferred: list[str]) -> list[str]:
    return [c for c in preferred if c in df.columns]


def build_basic_excel(df: pd.DataFrame, plant: str) -> bytes:
    df = clean_df(df)
    preferred = [
        "Plant", "Plant_part", "Plant_family", "Plant_synonyms", "Phytochemical_name",
        "Synonyms", "IMPPAT_ID", "PubChem_CID", "External_identifiers", "Molecular_formula",
        "MW_g_mol", "SMILES", "InChI", "InChIKey", "Source", "IMPPAT_plant_URL",
        "IMPPAT_detail_URL", "IMPPAT_reference"
    ]
    cols = pick_columns(df, preferred)
    basic = df[cols].copy() if cols else df.copy()
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        basic.to_excel(writer, index=False, sheet_name="Phytochemicals")
        pd.DataFrame({"Metric":["Plant searched","Plant-part association rows","Unique IMPPAT IDs","Rows with SMILES","RDKit available"],
                      "Value":[plant,len(df),df["IMPPAT_ID"].nunique() if "IMPPAT_ID" in df else 0,
                               int(df["SMILES"].fillna("").astype(str).str.strip().ne("").sum()) if "SMILES" in df else 0,
                               "Yes" if RDKIT_OK else "No"]}).to_excel(writer,index=False,sheet_name="Summary")
        _format_workbook(writer)
    return buf.getvalue()


def build_advanced_excel(df: pd.DataFrame, plant: str) -> bytes:
    df = clean_df(df)
    descriptor_cols = ["Plant","Plant_part","Phytochemical_name","IMPPAT_ID","SMILES","RDKit_valid_structure",
        "Molecular_formula","MW_g_mol","Exact_mass","XlogP","TPSA_A2","HBD","HBA","Rotatable_bonds",
        "Heavy_atoms","Carbon_atoms","Nitrogen_atoms","Oxygen_atoms","Sulfur_atoms","Halogen_atoms",
        "Ring_count","Aromatic_ring_count","Fraction_CSP3","QED"]
    classification_cols = ["Plant","Plant_part","Phytochemical_name","IMPPAT_ID","Functional_groups",
        "ClassyFire_Kingdom","ClassyFire_Superclass","ClassyFire_Class","ClassyFire_Subclass",
        "NPClassifier_Pathway","NPClassifier_Superclass","NPClassifier_Class","NP_Likeness"]
    source_cols = ["Plant","Plant_part","Phytochemical_name","IMPPAT_ID","Synonyms","External_identifiers",
        "PubChem_CID","IMPPAT_reference","IMPPAT_plant_URL","IMPPAT_detail_URL","Source"]
    basic_cols = ["Plant","Plant_part","Phytochemical_name","Synonyms","IMPPAT_ID","PubChem_CID",
        "Molecular_formula","MW_g_mol","SMILES","InChI","InChIKey","Source"]
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df[pick_columns(df,basic_cols) or list(df.columns)].to_excel(writer,index=False,sheet_name="Compound_Master")
        df[pick_columns(df,descriptor_cols)].to_excel(writer,index=False,sheet_name="Molecular_Descriptors")
        df[pick_columns(df,classification_cols)].to_excel(writer,index=False,sheet_name="Classifications")
        df[pick_columns(df,source_cols)].to_excel(writer,index=False,sheet_name="Sources_Identifiers")
        summary = pd.DataFrame({"Metric":["Plant searched","Association rows","Unique phytochemicals by IMPPAT ID","Records with SMILES","Records with valid RDKit structure","RDKit calculation available"],
            "Value":[plant,len(df),df["IMPPAT_ID"].nunique() if "IMPPAT_ID" in df else 0,
                int(df["SMILES"].fillna("").astype(str).str.strip().ne("").sum()) if "SMILES" in df else 0,
                int(df["RDKit_valid_structure"].astype(str).eq("Yes").sum()) if "RDKit_valid_structure" in df else 0,
                "Yes" if RDKIT_OK else "No"]})
        summary.to_excel(writer,index=False,sheet_name="Summary")
        _format_workbook(writer)
    return buf.getvalue()


def _format_workbook(writer):
    for ws in writer.book.worksheets:
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for cells in ws.columns:
            max_len = min(max((len(str(c.value or "")) for c in cells), default=10) + 2, 52)
            ws.column_dimensions[cells[0].column_letter].width = max(12, max_len)

