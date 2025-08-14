from health_score import HealthScoreCalculator, Gender, AgeGroup
from prettytable import PrettyTable
import json

def print_health_assessment(calculator: HealthScoreCalculator, score: float, system_scores: dict):
    """Print health assessment in a tabular format."""
    # Create main table for overall score
    main_table = PrettyTable()
    main_table.field_names = ["Overall Health Score", "Assessment"]
    main_table.add_row([f"{score:.1f}%", calculator.get_health_assessment(score)])
    main_table.align = "l"
    print("\nOverall Health Assessment")
    print("=" * 50)
    print(main_table)
    
    # Create table for system scores
    system_table = PrettyTable()
    system_table.field_names = ["System", "Score", "Status"]
    system_table.align = "l"
    
    for system_name, system_data in system_scores.items():
        system_score = system_data['score']
        status = "Good" if system_score >= 70 else "Needs Attention"
        system_table.add_row([
            system_name.title(),
            f"{system_score:.1f}%",
            status
        ])
    
    print("\nSystem-wise Breakdown")
    print("=" * 50)
    print(system_table)
    
    # Create table for biomarker details
    biomarker_table = PrettyTable()
    biomarker_table.field_names = ["System", "Organ", "Biomarker", "Score", "Status"]
    biomarker_table.align = "l"
    
    for system_name, system_data in system_scores.items():
        for organ_name, organ_data in system_data['organs'].items():
            for biomarker_name, biomarker_score in organ_data['biomarkers'].items():
                score = biomarker_score
                status = "Good" if score >= 70 else "Needs Attention"
                biomarker_table.add_row([
                    system_name.title(),
                    organ_name.title(),
                    biomarker_name.replace('_', ' ').title(),
                    f"{score:.1f}%",
                    status
                ])
    
    print("\nDetailed Biomarker Analysis")
    print("=" * 50)
    print(biomarker_table)

def test_health_score():
    # Initialize calculator
    calculator = HealthScoreCalculator()
    
    # Test data for an Indian patient
    test_data = {
        "phr_id": "TEST123",
        "age": 34.8,
        "gender": "male",
        "age_bucket": "18-39",
        "biomarkers": [
            {"loinc_id": "2089-1", "value": 110, "report_unit": "mg/dL"},  # LDL
            {"loinc_id": "2085-9", "value": 45, "report_unit": "mg/dL"},   # HDL
            {"loinc_id": "2093-3", "value": 180, "report_unit": "mg/dL"},  # Total Cholesterol
            {"loinc_id": "2571-8", "value": 120, "report_unit": "mg/dL"},  # Triglycerides
            {"loinc_id": "30522-7", "value": 1.5, "report_unit": "mg/L"},  # hs-CRP
            {"loinc_id": "4548-4", "value": 5.2, "report_unit": "%"},      # HbA1c
            {"loinc_id": "1558-6", "value": 85, "report_unit": "mg/dL"},   # Fasting Glucose
            {"loinc_id": "718-7", "value": 14.2, "report_unit": "g/dL"},   # Hemoglobin
            {"loinc_id": "26453-1", "value": 4.8, "report_unit": "10^6/uL"}, # RBC
            {"loinc_id": "6690-2", "value": 7.5, "report_unit": "10^3/uL"},  # WBC
            {"loinc_id": "13056-7", "value": 250, "report_unit": "10^3/uL"}, # Platelets
            {"loinc_id": "2160-0", "value": 0.9, "report_unit": "mg/dL"},   # Creatinine
            {"loinc_id": "6299-2", "value": 15, "report_unit": "mg/dL"},    # BUN
            {"loinc_id": "3016-3", "value": 2.5, "report_unit": "uIU/mL"},  # TSH
            {"loinc_id": "17861-6", "value": 9.5, "report_unit": "mg/dL"},  # Calcium
            {"loinc_id": "49045-0", "value": 35, "report_unit": "ng/mL"},   # Vitamin D
            {"loinc_id": "2885-2", "value": 7.2, "report_unit": "g/dL"},    # Total Protein
            {"loinc_id": "1751-7", "value": 4.2, "report_unit": "g/dL"},    # Albumin
            {"loinc_id": "2951-2", "value": 140, "report_unit": "mmol/L"},  # Sodium
            {"loinc_id": "6298-4", "value": 4.2, "report_unit": "mmol/L"},  # Potassium
            {"loinc_id": "1920-8", "value": 25, "report_unit": "U/L"},      # SGOT
            {"loinc_id": "1742-6", "value": 28, "report_unit": "U/L"},      # SGPT
            {"loinc_id": "1975-2", "value": 0.8, "report_unit": "mg/dL"},   # Total Bilirubin
            {"loinc_id": "2339-0", "value": 300, "report_unit": "mg/dL"},   # Fibrinogen
            {"loinc_id": "2345-7", "value": 8.5, "report_unit": "uIU/mL"},  # Insulin
            {"loinc_id": "2336-6", "value": 8.0, "report_unit": "ng/mL"},   # Folate
            {"loinc_id": "2331-7", "value": 8.5, "report_unit": "ng/mL"},   # Osteocalcin
            {"loinc_id": "2329-1", "value": 25, "report_unit": "mg/dL"},    # Prealbumin
            {"loinc_id": "2327-5", "value": 85, "report_unit": "ug/dL"},    # Zinc
            {"loinc_id": "2325-9", "value": 65, "report_unit": "U/L"}       # Amylase
        ]
    }
    
    # Calculate health score with explanations
    score, system_scores, biomarker_values, explanations = calculator.calculate_score_from_data(test_data, explain=True)
    
    # Print results
    print(f"\nOverall Health Score: {score:.1f}")
    print(f"Health Assessment: {calculator.get_health_assessment(score)}")
    
    print("\nSystem-wise Scores:")
    for system_name, system_data in system_scores.items():
        print(f"\n{system_name.title()} System (Score: {system_data['score']:.1f}):")
        for organ_name, organ_data in system_data['organs'].items():
            print(f"  {organ_name.title()} (Score: {organ_data['score']:.1f}):")
            for biomarker_name, biomarker_score in organ_data['biomarkers'].items():
                if biomarker_name in biomarker_values:
                    value = biomarker_values[biomarker_name]
                    if biomarker_name in explanations.get(system_name, {}).get(organ_name, {}):
                        explanation = explanations[system_name][organ_name][biomarker_name]
                        print(f"    {biomarker_name}: {value} (Score: {biomarker_score:.1f})")
                        print(f"      Normal Range: {explanation['normal_range']}")
                        print(f"      Optimal Range: {explanation['optimal_range']}")
                        if explanation['risk_factors']:
                            print(f"      Risk Factors: {explanation['risk_factors']}")
                        print(f"      Notes: {', '.join(explanation['notes'])}")

if __name__ == "__main__":
    test_health_score() 