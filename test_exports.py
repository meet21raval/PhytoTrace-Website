import io
import pandas as pd
from openpyxl import load_workbook
from exports import build_basic_excel, build_advanced_excel


def sample_df():
    return pd.DataFrame([{
        "Plant": "Rheum palmatum", "Plant_part": "Root", "Phytochemical_name": "Emodin",
        "IMPPAT_ID": "IMPPAT3_PHYID123", "Synonyms": "Example synonym", "PubChem_CID": "3220",
        "SMILES": "CC1=CC(=O)c2cc(O)cc(O)c2C(=O)C1=O", "InChI": "InChI=example",
        "InChIKey": "EXAMPLE", "Molecular_formula": "C15H10O5", "MW_g_mol": 270.24,
        "RDKit_valid_structure": "Yes", "XlogP": 1.4, "TPSA_A2": 94.8,
        "Functional_groups": "hydroxy; ketone", "ClassyFire_Class": "Anthraquinones",
        "IMPPAT_plant_URL": "https://example.org/plant", "Source": "IMPPAT"
    }])


def test_basic_excel_has_compound_and_summary_sheets():
    data = build_basic_excel(sample_df(), "Rheum palmatum")
    wb = load_workbook(io.BytesIO(data), read_only=True)
    assert "Phytochemicals" in wb.sheetnames
    assert "Summary" in wb.sheetnames
    assert wb["Phytochemicals"].max_row == 2


def test_advanced_excel_has_separated_research_sheets():
    data = build_advanced_excel(sample_df(), "Rheum palmatum")
    wb = load_workbook(io.BytesIO(data), read_only=True)
    assert {"Compound_Master", "Molecular_Descriptors", "Classifications", "Sources_Identifiers", "Summary"}.issubset(set(wb.sheetnames))
    assert wb["Molecular_Descriptors"].max_row == 2
