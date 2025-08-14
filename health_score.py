from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum
import math
from sklearn.linear_model import LinearRegression
from lifelines import CoxPHFitter
import pandas as pd

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

class AgeGroup(Enum):
    YOUNG = "18-39"
    MIDDLE = "40-59"
    SENIOR = "60+"

@dataclass
class RiskFactor:
    name: str
    weight: float
    threshold: float
    direction: str  # "higher" or "lower" indicates if higher/lower values increase risk

@dataclass
class Biomarker:
    name: str
    weight: float
    normal_range: tuple[float, float]
    unit: str
    optimal_range: Optional[tuple[float, float]] = None
    risk_factors: Dict[str, RiskFactor] = None
    scoring_algorithm: Optional[Callable] = None

    def __post_init__(self):
        if self.risk_factors is None:
            self.risk_factors = {}

@dataclass
class Organ:
    name: str
    weight: float
    biomarkers: Dict[str, Biomarker]

@dataclass
class System:
    name: str
    weight: float
    organs: Dict[str, Organ]

class LoincMapper:
    """Maps LOINC codes to biomarker names and handles unit conversions."""
    
    LOINC_MAP = {
        # Cardiovascular System
        "2089-1": {"name": "LDL", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "2085-9": {"name": "HDL", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "2093-3": {"name": "Total Cholesterol", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "2571-8": {"name": "Triglycerides", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "30522-7": {"name": "hs-CRP", "unit": "mg/L", "system": "cardiovascular", "organ": "heart"},
        "10835-7": {"name": "Lipo (a)", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "1869-7": {"name": "APO-A1", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "1884-6": {"name": "APO-B", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "1874-7": {"name": "APO-B/APO-A1", "unit": "ratio", "system": "cardiovascular", "organ": "heart"},
        "2339-0": {"name": "Fibrinogen", "unit": "mg/dL", "system": "cardiovascular", "organ": "heart"},
        "2338-2": {"name": "D-Dimer", "unit": "ng/mL", "system": "cardiovascular", "organ": "heart"},
        
        # Metabolic System
        "4548-4": {"name": "HbA1c", "unit": "%", "system": "metabolic", "organ": "pancreas"},
        "1558-6": {"name": "Glucose (Fasting)", "unit": "mg/dL", "system": "metabolic", "organ": "pancreas"},
        "13965-9": {"name": "Homocysteine", "unit": "umol/L", "system": "metabolic", "organ": "liver"},
        "2345-7": {"name": "Insulin", "unit": "uIU/mL", "system": "metabolic", "organ": "pancreas"},
        "2340-8": {"name": "C-Peptide", "unit": "ng/mL", "system": "metabolic", "organ": "pancreas"},
        "2335-8": {"name": "Leptin", "unit": "ng/mL", "system": "metabolic", "organ": "adipose"},
        
        # Hematological System
        "718-7": {"name": "Hemoglobin", "unit": "g/dL", "system": "hematological", "organ": "blood"},
        "26453-1": {"name": "RBC", "unit": "10^6/uL", "system": "hematological", "organ": "blood"},
        "6690-2": {"name": "WBC", "unit": "10^3/uL", "system": "hematological", "organ": "blood"},
        "13056-7": {"name": "Platelets", "unit": "10^3/uL", "system": "hematological", "organ": "blood"},
        "2498-4": {"name": "Iron", "unit": "ug/dL", "system": "hematological", "organ": "blood"},
        "3024-7": {"name": "TIBC", "unit": "ug/dL", "system": "hematological", "organ": "blood"},
        "20567-4": {"name": "Ferritin", "unit": "ng/mL", "system": "hematological", "organ": "blood"},
        "2132-9": {"name": "Vitamin B12", "unit": "pg/mL", "system": "hematological", "organ": "blood"},
        "2336-6": {"name": "Folate", "unit": "ng/mL", "system": "hematological", "organ": "blood"},
        "2337-4": {"name": "Vitamin B6", "unit": "ng/mL", "system": "hematological", "organ": "blood"},
        
        # Renal System
        "2160-0": {"name": "Creatinine", "unit": "mg/dL", "system": "renal", "organ": "kidney"},
        "6299-2": {"name": "BUN", "unit": "mg/dL", "system": "renal", "organ": "kidney"},
        "69405-9": {"name": "eGFR", "unit": "mL/min/1.73m2", "system": "renal", "organ": "kidney"},
        "32294-1": {"name": "Urinary Albumin/Creatinine ratio", "unit": "mg/g", "system": "renal", "organ": "kidney"},
        "14957-5": {"name": "Urinary microalbumin", "unit": "mg/L", "system": "renal", "organ": "kidney"},
        "2334-1": {"name": "Cystatin C", "unit": "mg/L", "system": "renal", "organ": "kidney"},
        
        # Endocrine System
        "3016-3": {"name": "TSH", "unit": "uIU/mL", "system": "endocrine", "organ": "thyroid"},
        "3053-6": {"name": "T3", "unit": "ng/dL", "system": "endocrine", "organ": "thyroid"},
        "3026-2": {"name": "T4", "unit": "ug/dL", "system": "endocrine", "organ": "thyroid"},
        "2333-3": {"name": "Cortisol", "unit": "ug/dL", "system": "endocrine", "organ": "adrenal"},
        "2332-5": {"name": "DHEA-S", "unit": "ug/dL", "system": "endocrine", "organ": "adrenal"},
        
        # Musculoskeletal System
        "17861-6": {"name": "Calcium", "unit": "mg/dL", "system": "musculoskeletal", "organ": "bone"},
        "49045-0": {"name": "Vitamin D", "unit": "ng/mL", "system": "musculoskeletal", "organ": "bone"},
        "2331-7": {"name": "Osteocalcin", "unit": "ng/mL", "system": "musculoskeletal", "organ": "bone"},
        "2330-9": {"name": "PTH", "unit": "pg/mL", "system": "musculoskeletal", "organ": "bone"},
        
        # Nutritional Health
        "2885-2": {"name": "Total Protein", "unit": "g/dL", "system": "nutritional", "organ": "liver"},
        "1751-7": {"name": "Albumin", "unit": "g/dL", "system": "nutritional", "organ": "liver"},
        "2329-1": {"name": "Prealbumin", "unit": "mg/dL", "system": "nutritional", "organ": "liver"},
        "2328-3": {"name": "Transferrin", "unit": "mg/dL", "system": "nutritional", "organ": "liver"},
        
        # Electrolytes & Minerals
        "2951-2": {"name": "Sodium", "unit": "mmol/L", "system": "electrolytes", "organ": "blood"},
        "6298-4": {"name": "Potassium", "unit": "mmol/L", "system": "electrolytes", "organ": "blood"},
        "2593-2": {"name": "Magnesium", "unit": "mg/dL", "system": "electrolytes", "organ": "blood"},
        "24519-1": {"name": "Phosphorus", "unit": "mg/dL", "system": "electrolytes", "organ": "blood"},
        "2327-5": {"name": "Zinc", "unit": "ug/dL", "system": "electrolytes", "organ": "blood"},
        "2326-7": {"name": "Copper", "unit": "ug/dL", "system": "electrolytes", "organ": "blood"},
        
        # Gastrointestinal System
        "1920-8": {"name": "SGOT", "unit": "U/L", "system": "gastrointestinal", "organ": "liver"},
        "1742-6": {"name": "SGPT", "unit": "U/L", "system": "gastrointestinal", "organ": "liver"},
        "2324-2": {"name": "GGT", "unit": "U/L", "system": "gastrointestinal", "organ": "liver"},
        "6768-6": {"name": "Alkaline Phosphatase", "unit": "U/L", "system": "gastrointestinal", "organ": "liver"},
        "1975-2": {"name": "Bilirubin - Total", "unit": "mg/dL", "system": "gastrointestinal", "organ": "liver"},
        "1968-7": {"name": "Bilirubin - Direct", "unit": "mg/dL", "system": "gastrointestinal", "organ": "liver"},
        "1971-1": {"name": "Bilirubin - Indirect", "unit": "mg/dL", "system": "gastrointestinal", "organ": "liver"},
        "3084-1": {"name": "Uric Acid", "unit": "mg/dL", "system": "gastrointestinal", "organ": "liver"},
        "2325-9": {"name": "Amylase", "unit": "U/L", "system": "gastrointestinal", "organ": "pancreas"},
        "2323-4": {"name": "Lipase", "unit": "U/L", "system": "gastrointestinal", "organ": "pancreas"}
    }

    # Add this mapping for LOINC biomarker names to internal keys
    NAME_TO_KEY = {
        # Cardiovascular
        "LDL": "ldl_c",
        "HDL": "hdl_c",
        "Total Cholesterol": "total_cholesterol",
        "Triglycerides": "triglycerides",
        "hs-CRP": "hs_crp",
        "Lipo (a)": "lipo_a",
        "APO-A1": "apo_a1",
        "APO-B": "apo_b",
        "APO-B/APO-A1": "apo_b_a1_ratio",
        "Fibrinogen": "fibrinogen",
        "D-Dimer": "d_dimer",
        
        # Metabolic
        "Glucose (Fasting)": "fasting_glucose",
        "HbA1c": "hba1c",
        "Homocysteine": "homocysteine",
        "Insulin": "insulin",
        "C-Peptide": "c_peptide",
        "Leptin": "leptin",
        
        # Hematological
        "Hemoglobin": "hemoglobin",
        "RBC": "rbc",
        "WBC": "wbc",
        "Platelets": "platelets",
        "Iron": "iron",
        "TIBC": "tibc",
        "Ferritin": "ferritin",
        "Vitamin B12": "vitamin_b12",
        "Folate": "folate",
        "Vitamin B6": "vitamin_b6",
        
        # Renal
        "Creatinine": "creatinine",
        "BUN": "bun",
        "eGFR": "egfr",
        "Urinary Albumin/Creatinine ratio": "uacr",
        "Urinary microalbumin": "microalbumin",
        "Cystatin C": "cystatin_c",
        
        # Endocrine
        "TSH": "tsh",
        "T3": "t3",
        "T4": "t4",
        "Cortisol": "cortisol",
        "DHEA-S": "dhea_s",
        
        # Musculoskeletal
        "Calcium": "calcium",
        "Vitamin D": "vitamin_d",
        "Osteocalcin": "osteocalcin",
        "PTH": "pth",
        
        # Nutritional
        "Total Protein": "total_protein",
        "Albumin": "albumin",
        "Prealbumin": "prealbumin",
        "Transferrin": "transferrin",
        
        # Electrolytes
        "Sodium": "sodium",
        "Potassium": "potassium",
        "Magnesium": "magnesium",
        "Phosphorus": "phosphorus",
        "Zinc": "zinc",
        "Copper": "copper",
        
        # Gastrointestinal
        "SGOT": "sgot",
        "SGPT": "sgpt",
        "GGT": "ggt",
        "Alkaline Phosphatase": "alk_phos",
        "Bilirubin - Total": "total_bilirubin",
        "Bilirubin - Direct": "direct_bilirubin",
        "Bilirubin - Indirect": "indirect_bilirubin",
        "Uric Acid": "uric_acid",
        "Amylase": "amylase",
        "Lipase": "lipase"
    }

    @staticmethod
    def convert_value(value: float, from_unit: str, to_unit: str) -> float:
        """Convert value from one unit to another."""
        if from_unit == to_unit:
            return value
        
        # Add conversion factors as needed
        conversions = {
            ("g/dL", "mg/dL"): 1000,
            ("mg/dL", "g/dL"): 0.001,
            ("ng/dL", "µg/dL"): 0.001,
            ("µg/dL", "ng/dL"): 1000,
        }
        
        conversion_key = (from_unit, to_unit)
        if conversion_key in conversions:
            return value * conversions[conversion_key]
        
        return value  # Return original value if conversion not found

    @classmethod
    def process_biomarkers(cls, biomarkers: List[Dict[str, Any]]) -> Dict[str, float]:
        """Process biomarkers from the input format to our internal format."""
        processed = {}
        
        for biomarker in biomarkers:
            loinc_id = biomarker["loinc_id"]
            if loinc_id in cls.LOINC_MAP:
                mapping = cls.LOINC_MAP[loinc_id]
                value = biomarker["value"]
                from_unit = biomarker["report_unit"]
                
                # Skip biomarkers with "not present" value
                if value == "not present":
                    continue
                
                # Convert value to target unit
                converted_value = cls.convert_value(value, from_unit, mapping["unit"])
                # Map to internal key if available
                key = cls.NAME_TO_KEY.get(mapping["name"], mapping["name"].lower().replace(' ', '_'))
                processed[key] = converted_value
        
        return processed

class HealthScoreCalculator:
    def __init__(self):
        self.systems = self._initialize_systems()
        self.age_gender_weights = self._initialize_age_gender_weights()
        self.risk_factors = {}
        # Build risk_factors dict from all biomarkers
        for system in self.systems.values():
            for organ in system.organs.values():
                for biomarker_name, biomarker in organ.biomarkers.items():
                    self.risk_factors[biomarker_name] = biomarker
        # Example: Pre-trained imputation and Cox models (in real use, train on real data)
        self.imputer_model = None
        self.cox_model = None
        self._initialize_dummy_models()

    def _initialize_systems(self) -> Dict[str, System]:
        """Initialize all systems with their organs and biomarkers."""
        # Cardiovascular System
        cardiovascular_system = System("Cardiovascular", 0.20, {
            "heart": Organ("Heart", 1.0, {
                "ldl_c": Biomarker(
                    "LDL-C", 
                    0.20, 
                    (0, 130),  # Indian range
                    "mg/dL",
                    optimal_range=(50, 100),  # Indian optimal
                    risk_factors={
                        "hdl_c": RiskFactor("HDL-C", -0.2, 40, "higher"),
                        "hs_crp": RiskFactor("hs-CRP", 0.3, 2.0, "higher"),
                        "triglycerides": RiskFactor("Triglycerides", 0.15, 150, "higher")
                    }
                ),
                "hdl_c": Biomarker(
                    "HDL-C", 
                    0.15, 
                    (35, 65),  # Indian range
                    "mg/dL",
                    optimal_range=(40, 60),  # Indian optimal
                    risk_factors={
                        "triglycerides": RiskFactor("Triglycerides", -0.15, 150, "higher"),
                        "ldl_c": RiskFactor("LDL-C", -0.1, 130, "higher")
                    }
                ),
                "total_cholesterol": Biomarker(
                    "Total Cholesterol", 
                    0.15, 
                    (125, 250),  # Indian range
                    "mg/dL",
                    optimal_range=(150, 200),  # Indian optimal
                    risk_factors={
                        "hdl_c": RiskFactor("HDL-C", -0.2, 40, "higher"),
                        "ldl_c": RiskFactor("LDL-C", 0.3, 130, "higher")
                    }
                ),
                "triglycerides": Biomarker(
                    "Triglycerides", 
                    0.15, 
                    (0, 200),  # Indian range
                    "mg/dL",
                    optimal_range=(50, 150),  # Indian optimal
                    risk_factors={
                        "hdl_c": RiskFactor("HDL-C", -0.2, 40, "higher"),
                        "fasting_glucose": RiskFactor("Fasting Glucose", 0.2, 100, "higher")
                    }
                ),
                "hs_crp": Biomarker(
                    "hs-CRP", 
                    0.10, 
                    (0, 3), 
                    "mg/L",
                    optimal_range=(0, 1),
                    risk_factors={
                        "ldl_c": RiskFactor("LDL-C", 0.2, 130, "higher"),
                        "triglycerides": RiskFactor("Triglycerides", 0.15, 150, "higher")
                    }
                ),
                "lipo_a": Biomarker(
                    "Lipo (a)", 
                    0.05, 
                    (0, 30), 
                    "mg/dL",
                    optimal_range=(0, 10),
                    risk_factors={
                        "ldl_c": RiskFactor("LDL-C", 0.2, 130, "higher")
                    }
                ),
                "fibrinogen": Biomarker(
                    "Fibrinogen", 
                    0.05, 
                    (200, 400), 
                    "mg/dL",
                    optimal_range=(200, 350),
                    risk_factors={
                        "hs_crp": RiskFactor("hs-CRP", 0.2, 2.0, "higher")
                    }
                ),
                "d_dimer": Biomarker(
                    "D-Dimer", 
                    0.05, 
                    (0, 500), 
                    "ng/mL",
                    optimal_range=(0, 250)
                )
            })
        })
        
        # Metabolic System
        metabolic_system = System("Metabolic", 0.15, {
            "pancreas": Organ("Pancreas", 0.6, {
                "fasting_glucose": Biomarker(
                    "Fasting Glucose", 
                    0.25, 
                    (70, 110),  # Indian range
                    "mg/dL",
                    optimal_range=(75, 95),  # Indian optimal
                    risk_factors={
                        "hba1c": RiskFactor("HbA1c", 0.3, 5.7, "higher"),
                        "triglycerides": RiskFactor("Triglycerides", 0.2, 150, "higher"),
                        "hdl_c": RiskFactor("HDL-C", -0.15, 40, "higher")
                    }
                ),
                "hba1c": Biomarker(
                    "HbA1c", 
                    0.25, 
                    (4.0, 6.0),  # Indian range
                    "%",
                    optimal_range=(4.5, 5.5),  # Indian optimal
                    risk_factors={
                        "fasting_glucose": RiskFactor("Fasting Glucose", 0.3, 110, "higher")
                    }
                ),
                "insulin": Biomarker(
                    "Insulin", 
                    0.25, 
                    (2.6, 24.9), 
                    "uIU/mL",
                    optimal_range=(3.0, 20.0),
                    risk_factors={
                        "fasting_glucose": RiskFactor("Fasting Glucose", 0.2, 100, "higher")
                    }
                ),
                "c_peptide": Biomarker(
                    "C-Peptide", 
                    0.25, 
                    (0.8, 3.1), 
                    "ng/mL",
                    optimal_range=(1.0, 2.5)
                )
            }),
            "liver": Organ("Liver", 0.4, {
                "homocysteine": Biomarker(
                    "Homocysteine", 
                    0.50, 
                    (0, 15), 
                    "umol/L",
                    optimal_range=(0, 10),
                    risk_factors={
                        "vitamin_b12": RiskFactor("Vitamin B12", -0.2, 200, "lower")
                    }
                ),
                "leptin": Biomarker(
                    "Leptin", 
                    0.50, 
                    (0.5, 15.2), 
                    "ng/mL",
                    optimal_range=(1.0, 12.0)
                )
            })
        })
        
        # Hematological System
        hematological_system = System("Hematological", 0.12, {
            "blood": Organ("Blood", 1.0, {
                "hemoglobin": Biomarker(
                    "Hemoglobin", 
                    0.15, 
                    (12.0, 16.0),  # Indian range
                    "g/dL",
                    optimal_range=(13.0, 15.0)  # Indian optimal
                ),
                "rbc": Biomarker(
                    "RBC", 
                    0.15, 
                    (4.0, 5.5),  # Indian range
                    "10^6/uL",
                    optimal_range=(4.2, 5.2)  # Indian optimal
                ),
                "wbc": Biomarker(
                    "WBC", 
                    0.10, 
                    (4.0, 11.0), 
                    "10^3/uL",
                    optimal_range=(5.0, 10.0)
                ),
                "platelets": Biomarker(
                    "Platelets", 
                    0.10, 
                    (150, 450), 
                    "10^3/uL",
                    optimal_range=(200, 400)
                ),
                "iron": Biomarker(
                    "Iron", 
                    0.10, 
                    (50, 150),  # Indian range
                    "ug/dL",
                    optimal_range=(60, 140)  # Indian optimal
                ),
                "tibc": Biomarker(
                    "TIBC", 
                    0.10, 
                    (240, 450), 
                    "ug/dL",
                    optimal_range=(250, 400)
                ),
                "ferritin": Biomarker(
                    "Ferritin", 
                    0.10, 
                    (30, 400), 
                    "ng/mL",
                    optimal_range=(50, 300)
                ),
                "vitamin_b12": Biomarker(
                    "Vitamin B12", 
                    0.10, 
                    (200, 900), 
                    "pg/mL",
                    optimal_range=(300, 800)
                ),
                "folate": Biomarker(
                    "Folate", 
                    0.10, 
                    (2.0, 20.0), 
                    "ng/mL",
                    optimal_range=(3.0, 15.0)
                ),
                "vitamin_b6": Biomarker(
                    "Vitamin B6", 
                    0.10, 
                    (5.0, 50.0), 
                    "ng/mL",
                    optimal_range=(8.0, 40.0)
                )
            })
        })
        
        # Renal System
        renal_system = System("Renal", 0.10, {
            "kidney": Organ("Kidney", 1.0, {
                "creatinine": Biomarker(
                    "Creatinine", 
                    0.20, 
                    (0.5, 1.2),  # Indian range
                    "mg/dL",
                    optimal_range=(0.6, 1.1)  # Indian optimal
                ),
                "bun": Biomarker(
                    "BUN", 
                    0.20, 
                    (7, 20), 
                    "mg/dL",
                    optimal_range=(8, 18)
                ),
                "egfr": Biomarker(
                    "eGFR", 
                    0.20, 
                    (90, 120), 
                    "mL/min/1.73m2",
                    optimal_range=(90, 120)
                ),
                "uacr": Biomarker(
                    "Urinary Albumin/Creatinine ratio", 
                    0.20, 
                    (0, 30), 
                    "mg/g",
                    optimal_range=(0, 20)
                ),
                "cystatin_c": Biomarker(
                    "Cystatin C", 
                    0.20, 
                    (0.53, 0.95), 
                    "mg/L",
                    optimal_range=(0.53, 0.82)
                )
            })
        })
        
        # Endocrine System
        endocrine_system = System("Endocrine", 0.08, {
            "thyroid": Organ("Thyroid", 0.6, {
                "tsh": Biomarker(
                    "TSH", 
                    0.40, 
                    (0.4, 4.0), 
                    "uIU/mL",
                    optimal_range=(0.5, 3.0)
                ),
                "t3": Biomarker(
                    "T3", 
                    0.30, 
                    (80, 200), 
                    "ng/dL",
                    optimal_range=(100, 180)
                ),
                "t4": Biomarker(
                    "T4", 
                    0.30, 
                    (4.5, 12.0), 
                    "ug/dL",
                    optimal_range=(5.0, 11.0)
                )
            }),
            "adrenal": Organ("Adrenal", 0.4, {
                "cortisol": Biomarker(
                    "Cortisol", 
                    0.50, 
                    (6.2, 19.4), 
                    "ug/dL",
                    optimal_range=(7.0, 18.0)
                ),
                "dhea_s": Biomarker(
                    "DHEA-S", 
                    0.50, 
                    (35, 430), 
                    "ug/dL",
                    optimal_range=(50, 400)
                )
            })
        })
        
        # Musculoskeletal System
        musculoskeletal_system = System("Musculoskeletal", 0.08, {
            "bone": Organ("Bone", 1.0, {
                "calcium": Biomarker(
                    "Calcium", 
                    0.25, 
                    (8.5, 10.5), 
                    "mg/dL",
                    optimal_range=(9.0, 10.0)
                ),
                "vitamin_d": Biomarker(
                    "Vitamin D", 
                    0.25, 
                    (20, 100),  # Indian range
                    "ng/mL",
                    optimal_range=(30, 80)  # Indian optimal
                ),
                "osteocalcin": Biomarker(
                    "Osteocalcin", 
                    0.25, 
                    (3.0, 13.7), 
                    "ng/mL",
                    optimal_range=(4.0, 12.0)
                ),
                "pth": Biomarker(
                    "PTH", 
                    0.25, 
                    (15, 65), 
                    "pg/mL",
                    optimal_range=(20, 60)
                )
            })
        })
        
        # Nutritional System
        nutritional_system = System("Nutritional", 0.07, {
            "liver": Organ("Liver", 1.0, {
                "total_protein": Biomarker(
                    "Total Protein", 
                    0.25, 
                    (6.0, 8.3), 
                    "g/dL",
                    optimal_range=(6.5, 8.0)
                ),
                "albumin": Biomarker(
                    "Albumin", 
                    0.25, 
                    (3.5, 5.0), 
                    "g/dL",
                    optimal_range=(3.8, 4.8)
                ),
                "prealbumin": Biomarker(
                    "Prealbumin", 
                    0.25, 
                    (15, 36), 
                    "mg/dL",
                    optimal_range=(18, 34)
                ),
                "transferrin": Biomarker(
                    "Transferrin", 
                    0.25, 
                    (200, 360), 
                    "mg/dL",
                    optimal_range=(220, 340)
                )
            })
        })
        
        # Electrolytes System
        electrolytes_system = System("Electrolytes", 0.07, {
            "blood": Organ("Blood", 1.0, {
                "sodium": Biomarker(
                    "Sodium", 
                    0.20, 
                    (135, 145), 
                    "mmol/L",
                    optimal_range=(136, 144)
                ),
                "potassium": Biomarker(
                    "Potassium", 
                    0.20, 
                    (3.5, 5.0), 
                    "mmol/L",
                    optimal_range=(3.6, 4.8)
                ),
                "magnesium": Biomarker(
                    "Magnesium", 
                    0.20, 
                    (1.7, 2.2), 
                    "mg/dL",
                    optimal_range=(1.8, 2.1)
                ),
                "phosphorus": Biomarker(
                    "Phosphorus", 
                    0.20, 
                    (2.5, 4.5), 
                    "mg/dL",
                    optimal_range=(2.8, 4.2)
                ),
                "zinc": Biomarker(
                    "Zinc", 
                    0.10, 
                    (70, 120), 
                    "ug/dL",
                    optimal_range=(75, 115)
                ),
                "copper": Biomarker(
                    "Copper", 
                    0.10, 
                    (70, 140), 
                    "ug/dL",
                    optimal_range=(75, 135)
                )
            })
        })
        
        # Gastrointestinal System
        gastrointestinal_system = System("Gastrointestinal", 0.08, {
            "liver": Organ("Liver", 0.7, {
                "sgot": Biomarker(
                    "SGOT", 
                    0.15, 
                    (0, 40), 
                    "U/L",
                    optimal_range=(0, 35)
                ),
                "sgpt": Biomarker(
                    "SGPT", 
                    0.15, 
                    (0, 40), 
                    "U/L",
                    optimal_range=(0, 35)
                ),
                "ggt": Biomarker(
                    "GGT", 
                    0.15, 
                    (0, 65), 
                    "U/L",
                    optimal_range=(0, 50)
                ),
                "alk_phos": Biomarker(
                    "Alkaline Phosphatase", 
                    0.15, 
                    (44, 147), 
                    "U/L",
                    optimal_range=(50, 130)
                ),
                "total_bilirubin": Biomarker(
                    "Bilirubin - Total", 
                    0.10, 
                    (0.1, 1.2), 
                    "mg/dL",
                    optimal_range=(0.2, 1.0)
                ),
                "direct_bilirubin": Biomarker(
                    "Bilirubin - Direct", 
                    0.10, 
                    (0.0, 0.3), 
                    "mg/dL",
                    optimal_range=(0.0, 0.2)
                ),
                "indirect_bilirubin": Biomarker(
                    "Bilirubin - Indirect", 
                    0.10, 
                    (0.0, 0.9), 
                    "mg/dL",
                    optimal_range=(0.0, 0.7)
                ),
                "uric_acid": Biomarker(
                    "Uric Acid", 
                    0.10, 
                    (3.5, 7.2), 
                    "mg/dL",
                    optimal_range=(3.8, 6.8)
                )
            }),
            "pancreas": Organ("Pancreas", 0.3, {
                "amylase": Biomarker(
                    "Amylase", 
                    0.50, 
                    (30, 110), 
                    "U/L",
                    optimal_range=(40, 100)
                ),
                "lipase": Biomarker(
                    "Lipase", 
                    0.50, 
                    (0, 160), 
                    "U/L",
                    optimal_range=(10, 140)
                )
            })
        })
        
        systems = {
            "cardiovascular": cardiovascular_system,
            "metabolic": metabolic_system,
            "hematological": hematological_system,
            "renal": renal_system,
            "endocrine": endocrine_system,
            "musculoskeletal": musculoskeletal_system,
            "nutritional": nutritional_system,
            "electrolytes": electrolytes_system,
            "gastrointestinal": gastrointestinal_system
        }
        return systems

    def _initialize_age_gender_weights(self):
        """Initialize age-gender specific weights for each system."""
        return {
            "male_18-39": {
                "cardiovascular": 0.25,
                "metabolic": 0.18,
                "hematological": 0.12,
                "renal": 0.09,
                "endocrine": 0.06,
                "musculoskeletal": 0.08,
                "nutritional": 0.05,
                "electrolytes": 0.05,
                "gastrointestinal": 0.10
            },
            "male_40-59": {
                "cardiovascular": 0.28,
                "metabolic": 0.17,
                "hematological": 0.12,
                "renal": 0.10,
                "endocrine": 0.07,
                "musculoskeletal": 0.08,
                "nutritional": 0.05,
                "electrolytes": 0.05,
                "gastrointestinal": 0.09
            },
            "male_60+": {
                "cardiovascular": 0.30,
                "metabolic": 0.19,
                "hematological": 0.11,
                "renal": 0.12,
                "endocrine": 0.09,
                "musculoskeletal": 0.07,
                "nutritional": 0.05,
                "electrolytes": 0.04,
                "gastrointestinal": 0.08
            },
            "female_18-39": {
                "cardiovascular": 0.24,
                "metabolic": 0.18,
                "hematological": 0.12,
                "renal": 0.10,
                "endocrine": 0.07,
                "musculoskeletal": 0.08,
                "nutritional": 0.06,
                "electrolytes": 0.05,
                "gastrointestinal": 0.10
            },
            "female_40-59": {
                "cardiovascular": 0.27,
                "metabolic": 0.18,
                "hematological": 0.12,
                "renal": 0.11,
                "endocrine": 0.08,
                "musculoskeletal": 0.08,
                "nutritional": 0.06,
                "electrolytes": 0.05,
                "gastrointestinal": 0.09
            },
            "female_60+": {
                "cardiovascular": 0.29,
                "metabolic": 0.20,
                "hematological": 0.11,
                "renal": 0.13,
                "endocrine": 0.10,
                "musculoskeletal": 0.07,
                "nutritional": 0.06,
                "electrolytes": 0.04,
                "gastrointestinal": 0.08
            }
        }

    def _sigmoid_score(self, x: float, center: float, width: float) -> float:
        """Calculate score using sigmoid function for smooth transitions."""
        # Prevent division by zero by ensuring minimum width
        min_width = 0.1  # Minimum width to prevent division by zero
        adjusted_width = max(abs(width), min_width)
        
        # Handle edge cases
        if x == center:
            return 1.0
        elif width == 0:
            return 1.0 if x == center else 0.0
        
        return 1 / (1 + math.exp((x - center) / adjusted_width))

    def _calculate_ldl_score(self, value: float, related_values: Dict[str, float]) -> float:
        """Calculate LDL-C score with sophisticated risk assessment."""
        # Base score using sigmoid
        base_score = self._sigmoid_score(value, 70, 15)
        
        # Calculate risk factors
        risk_score = 0
        if "hdl_c" in related_values:
            hdl = related_values["hdl_c"]
            if hdl < 40:
                risk_score += 0.2
            elif hdl < 50:
                risk_score += 0.1
        
        if "hs_crp" in related_values:
            crp = related_values["hs_crp"]
            if crp > 2.0:
                risk_score += 0.3
            elif crp > 1.0:
                risk_score += 0.15
        
        if "triglycerides" in related_values:
            trig = related_values["triglycerides"]
            if trig > 150:
                risk_score += 0.15
            elif trig > 100:
                risk_score += 0.075
        
        # Apply risk adjustment (capped at 40% reduction)
        final_score = max(0.6, base_score - risk_score)
        return final_score

    def _calculate_glucose_score(self, value: float, related_values: Dict[str, float]) -> float:
        """Calculate glucose score with sophisticated risk assessment."""
        # Base score using sigmoid
        base_score = self._sigmoid_score(value, 85, 10)
        
        # Calculate risk factors
        risk_score = 0
        if "hba1c" in related_values:
            hba1c = related_values["hba1c"]
            if hba1c > 5.7:
                risk_score += 0.3
            elif hba1c > 5.4:
                risk_score += 0.15
        
        if "triglycerides" in related_values:
            trig = related_values["triglycerides"]
            if trig > 150:
                risk_score += 0.2
            elif trig > 100:
                risk_score += 0.1
        
        if "hdl_c" in related_values:
            hdl = related_values["hdl_c"]
            if hdl < 40:
                risk_score += 0.15
            elif hdl < 50:
                risk_score += 0.075
        
        # Apply risk adjustment (capped at 40% reduction)
        final_score = max(0.6, base_score - risk_score)
        return final_score

    def _calculate_biomarker_score(self, biomarker_name: str, value: float, system_name: str, organ_name: str) -> Tuple[float, Dict]:
        """Calculate score for a single biomarker with detailed explanation."""
        if biomarker_name not in self.systems[system_name].organs[organ_name].biomarkers:
            return 50.0, {  # Return middle score instead of 0
                'value': value,
                'normal_range': 'Not defined',
                'optimal_range': 'Not defined',
                'score': 50.0,
                'risk_factors': [],
                'notes': ['Biomarker not defined in system']
            }
        
        biomarker = self.systems[system_name].organs[organ_name].biomarkers[biomarker_name]
        normal_range = biomarker.normal_range
        optimal_range = biomarker.optimal_range
        
        # Calculate base score using sigmoid function
        # Map value to 0-1 range relative to normal range
        x = (value - normal_range[0]) / (normal_range[1] - normal_range[0])
        # Use sigmoid function for smooth scoring, scaled to 0-100
        score = 100 / (1 + math.exp(-10 * (x - 0.5)))
        
        notes = []
        if value < normal_range[0]:
            notes.append(f"Value {value} below normal range {normal_range[0]}")
            # Instead of 0, give a score based on how far below normal
            distance = (normal_range[0] - value) / normal_range[0]
            score = max(10, 100 * (1 - min(1, distance)))
        elif value > normal_range[1]:
            notes.append(f"Value {value} above normal range {normal_range[1]}")
            # Instead of 0, give a score based on how far above normal
            distance = (value - normal_range[1]) / normal_range[1]
            score = max(10, 100 * (1 - min(1, distance)))
        else:
            if value < optimal_range[0]:
                notes.append(f"Value {value} below optimal range {optimal_range[0]}")
            elif value > optimal_range[1]:
                notes.append(f"Value {value} above optimal range {optimal_range[1]}")
            else:
                notes.append(f"Value {value} within optimal range {optimal_range[0]}-{optimal_range[1]}")
            notes.append(f"Sigmoid score: {score:.2f}")
        
        # Apply risk factor adjustments
        risk_factors = []
        biomarker_risk_factors = biomarker.risk_factors if biomarker.risk_factors else {}
        for risk_factor, adjustment in biomarker_risk_factors.items():
            if risk_factor in self.biomarker_values:
                risk_value = self.biomarker_values[risk_factor]
                risk_factor_obj = self.risk_factors[risk_factor]
                if risk_value < risk_factor_obj.normal_range[0]:
                    adjustment_value = adjustment[0]
                    risk_factors.append(f"{risk_factor}: {risk_value} < {risk_factor_obj.normal_range[0]} (weight {adjustment_value})")
                    score *= (1 + adjustment_value)
                elif risk_value > risk_factor_obj.normal_range[1]:
                    adjustment_value = adjustment[1]
                    risk_factors.append(f"{risk_factor}: {risk_value} > {risk_factor_obj.normal_range[1]} (weight {adjustment_value})")
                    score *= (1 + adjustment_value)
        
        # Ensure score stays within 0-100 range
        score = max(10, min(100, score))
        
        return score, {
            'value': value,
            'normal_range': normal_range,
            'optimal_range': optimal_range,
            'score': score,
            'risk_factors': risk_factors,
            'notes': notes
        }

    def calculate_organ_score(
        self, 
        organ: Organ, 
        biomarker_values: Dict[str, float],
        explain: bool = False
    ) -> (float, Dict[str, float], Dict[str, dict]):
        """Calculate score for an organ based on its biomarkers with detailed breakdown and explanations."""
        # Normalize biomarker weights
        total_biomarker_weight = sum(b.weight for b in organ.biomarkers.values())
        normalized_weights = {name: (b.weight / total_biomarker_weight if total_biomarker_weight > 0 else 1/len(organ.biomarkers)) for name, b in organ.biomarkers.items()}
        weighted_score = 0
        biomarker_scores = {}
        biomarker_explanations = {}
        # Find the system and organ names
        system_name = None
        organ_name = None
        for sys_name, system in self.systems.items():
            for org_name, org in system.organs.items():
                if org == organ:
                    system_name = sys_name
                    organ_name = org_name
                    break
            if system_name:
                break
        if not system_name or not organ_name:
            raise ValueError(f"Organ {organ.name} not found in any system")
        for biomarker_name, biomarker in organ.biomarkers.items():
            if biomarker_name in biomarker_values:
                try:
                    related_values = {
                        name: value for name, value in biomarker_values.items()
                        if name in biomarker.risk_factors if biomarker.risk_factors
                    }
                    if explain:
                        score, explanation = self._calculate_biomarker_score(
                            biomarker_name, 
                            biomarker_values[biomarker_name],
                            system_name,
                            organ_name
                        )
                        biomarker_explanations[biomarker_name] = explanation
                    else:
                        score, _ = self._calculate_biomarker_score(
                            biomarker_name, 
                            biomarker_values[biomarker_name],
                            system_name,
                            organ_name
                        )
                    weighted_score += score * normalized_weights[biomarker_name]
                    biomarker_scores[biomarker_name] = score
                except Exception as e:
                    print(f"Error calculating score for {biomarker_name}: {str(e)}")
                    score = 50.0
                    weighted_score += score * normalized_weights[biomarker_name]
                    biomarker_scores[biomarker_name] = score
                    if explain:
                        biomarker_explanations[biomarker_name] = {
                            'value': biomarker_values[biomarker_name],
                            'normal_range': getattr(biomarker, 'normal_range', 'Not defined'),
                            'optimal_range': getattr(biomarker, 'optimal_range', 'Not defined'),
                            'score': score,
                            'risk_factors': [],
                            'notes': [f'Error: {str(e)}']
                        }
        final_score = weighted_score if len(organ.biomarkers) > 0 else 50.0
        return (final_score, biomarker_scores, biomarker_explanations) if explain else (final_score, biomarker_scores)

    def calculate_system_score(
        self, 
        system: System, 
        biomarker_values: Dict[str, float],
        explain: bool = False
    ) -> (float, Dict[str, Dict[str, float]], Dict[str, Dict[str, dict]]):
        """Calculate score for a system with detailed organ and biomarker breakdown and explanations."""
        # Normalize organ weights
        total_organ_weight = sum(o.weight for o in system.organs.values())
        normalized_weights = {name: (o.weight / total_organ_weight if total_organ_weight > 0 else 1/len(system.organs)) for name, o in system.organs.items()}
        weighted_score = 0
        organ_scores = {}
        organ_explanations = {}
        for organ_name, organ in system.organs.items():
            if explain:
                score, biomarker_scores, biomarker_explanations = self.calculate_organ_score(organ, biomarker_values, explain=True)
                organ_explanations[organ_name] = biomarker_explanations
            else:
                score, biomarker_scores = self.calculate_organ_score(organ, biomarker_values)
            weighted_score += score * normalized_weights[organ_name]
            organ_scores[organ_name] = {
                "score": score,
                "biomarkers": biomarker_scores
            }
        final_score = weighted_score if len(system.organs) > 0 else 50.0
        return (final_score, organ_scores, organ_explanations) if explain else (final_score, organ_scores)

    def calculate_overall_health_score(
        self,
        biomarker_values: Dict[str, float],
        age_group: AgeGroup,
        gender: Gender,
        explain: bool = False
    ) -> (float, Dict[str, Dict[str, Dict[str, float]]], Dict[str, Dict[str, Dict[str, dict]]]):
        """Calculate overall health score with detailed system, organ, and biomarker breakdown and explanations."""
        key = f"{gender.value}_{age_group.value}"
        adjusted_weights = self.age_gender_weights[key]
        
        # Normalize system weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        normalized_weights = {name: weight/total_weight for name, weight in adjusted_weights.items()}
        
        total_score = 0
        system_scores = {}
        system_explanations = {}
        
        for system_name, system in self.systems.items():
            if explain:
                system_score, organ_scores, organ_explanations = self.calculate_system_score(system, biomarker_values, explain=True)
                system_explanations[system_name] = organ_explanations
            else:
                system_score, organ_scores = self.calculate_system_score(system, biomarker_values)
            
            # Use normalized weight
            adjusted_weight = normalized_weights[system_name]
            total_score += system_score * adjusted_weight
            
            system_scores[system_name] = {
                "score": system_score,  # Don't multiply by 100
                "organs": organ_scores
            }
        
        return (total_score, system_scores, system_explanations) if explain else (total_score, system_scores)

    def get_health_assessment(self, score: float) -> str:
        """Get health assessment based on the calculated score."""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Needs Attention"

    def _initialize_dummy_models(self):
        # Dummy imputer: Linear regression using available biomarkers
        X = pd.DataFrame({
            'ldl_c': [80, 100, 120, 140, 160],
            'triglycerides': [70, 90, 110, 130, 150]
        })
        y = [60, 55, 50, 45, 40]  # Fake HDL-C values
        self.imputer_model = LinearRegression().fit(X, y)
        
        # Dummy Cox model with more stable data
        try:
            df = pd.DataFrame({
                'age': [30, 40, 50, 60, 70],
                'ldl_c': [80, 100, 120, 140, 160],
                'hdl_c': [60, 55, 50, 45, 40],
                'event': [1, 0, 1, 0, 1],
                'duration': [5, 6, 4, 7, 3]
            })
            self.cox_model = CoxPHFitter()
            self.cox_model.fit(df, duration_col='duration', event_col='event')
        except Exception as e:
            print(f"Warning: Could not initialize Cox model: {str(e)}")
            self.cox_model = None

    def impute_missing_biomarkers(self, biomarker_values: Dict[str, float]) -> Dict[str, float]:
        # Example: Impute HDL-C if missing using LDL-C and Triglycerides
        if 'hdl_c' not in biomarker_values and 'ldl_c' in biomarker_values and 'triglycerides' in biomarker_values:
            X_pred = pd.DataFrame({
                'ldl_c': [biomarker_values['ldl_c']],
                'triglycerides': [biomarker_values['triglycerides']]
            })
            biomarker_values['hdl_c'] = float(self.imputer_model.predict(X_pred)[0])
        return biomarker_values

    def predict_future_risk(self, data: Dict[str, float]) -> float:
        """Predict 5-year risk using Cox model with fallback."""
        if self.cox_model is None:
            # Fallback to a simple risk calculation based on age and LDL
            age = data.get('age', 50)
            ldl = data.get('ldl_c', 120)
            hdl = data.get('hdl_c', 50)
            
            # Simple risk calculation
            age_risk = min(1.0, age / 100)  # Age risk increases with age
            ldl_risk = min(1.0, ldl / 200)  # LDL risk increases with LDL
            hdl_protection = max(0, 1 - (hdl / 100))  # HDL provides protection
            
            # Combine risks
            risk = (age_risk * 0.4 + ldl_risk * 0.4 + hdl_protection * 0.2)
            return min(0.95, max(0.05, risk))  # Keep risk between 5% and 95%
        
        try:
            # Try Cox model prediction
            X = pd.DataFrame({
                'age': [data.get('age', 50)],
                'ldl_c': [data.get('ldl_c', 120)],
                'hdl_c': [data.get('hdl_c', 50)]
            })
            survival_prob = self.cox_model.predict_survival_function(X, times=[5]).values[0][0]
            return 1 - survival_prob
        except Exception as e:
            print(f"Warning: Cox model prediction failed: {str(e)}")
            # Fallback to simple risk calculation
            return self.predict_future_risk(data)  # This will use the fallback logic

    def calculate_score_from_data(self, data: Dict[str, Any], explain: bool = False) -> (float, dict, dict, dict):
        """Calculate health score from input data with detailed explanations."""
        # Process biomarkers
        self.biomarker_values = LoincMapper.process_biomarkers(data["biomarkers"])
        
        # Get age group and gender
        age = data["age"]
        gender = Gender(data["gender"].lower())
        
        if age < 40:
            age_group = AgeGroup.YOUNG
        elif age < 60:
            age_group = AgeGroup.MIDDLE
        else:
            age_group = AgeGroup.SENIOR
        
        # Calculate overall score
        score, system_scores, system_explanations = self.calculate_overall_health_score(
            self.biomarker_values,
            age_group,
            gender,
            explain=explain
        )
        
        return score, system_scores, self.biomarker_values, system_explanations if explain else {} 