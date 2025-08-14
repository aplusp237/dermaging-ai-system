#!/usr/bin/env python3
"""
DermAging Two-Stage Pipeline - Sample Execution
This script demonstrates the exact two-stage pipeline as specified in the prompt.
"""

import json
import time
from typing import Dict, Any

def stage1_llava_clinical_vision_analysis(image_paths: Dict[str, str], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Stage 1: LLaVA Clinical Vision Analysis (VISION-ONLY)
    
    Model: LLaVA (local)
    Role: Read uploaded images, detect faces, segment facial zones, extract visual observations
    Constraints: NO diagnoses, scores, or medical recommendations
    Output: Purely visual observations + zone findings + quality notes
    """
    
    print("🔍 STAGE 1: LLaVA Clinical Vision Analysis")
    print("=" * 50)
    print("Processing images with LLaVA...")
    print(f"- Frontal image: {image_paths.get('frontal', 'Not provided')}")
    print(f"- Left profile: {image_paths.get('left_profile', 'Not provided')}")
    print(f"- Right profile: {image_paths.get('right_profile', 'Not provided')}")
    
    # Simulate LLaVA processing time
    time.sleep(2)
    
    # Mock LLaVA clinical vision findings (exactly as specified in prompt)
    findings = {
        "age_estimation": "late 30s–early 40s",
        "zone_analysis": {
            "forehead": {
                "fine_lines_wrinkles": "Horizontal lines visible at rest, moderate depth",
                "texture_coarseness": "Slightly coarse texture with visible pores",
                "pigment_spots": "Few scattered age spots, mild solar damage",
                "redness_erythema": "Minimal erythema, even skin tone",
                "pore_visibility": "Moderately visible pores, consistent with age",
                "sebum_shine": "Minimal sebum production in T-zone",
                "hydration_dryness": "Adequate hydration, no significant dryness"
            },
            "periorbital": {
                "fine_lines_wrinkles": "Crow's feet present, moderate depth",
                "texture_coarseness": "Fine texture, some crepiness",
                "pigment_spots": "Mild under-eye darkness, possible PIH",
                "redness_erythema": "Minimal, some vascular showing",
                "pore_visibility": "Very fine pores",
                "sebum_shine": "Minimal sebum",
                "hydration_dryness": "Slight dryness, normal for area"
            },
            "cheek_left": {
                "fine_lines_wrinkles": "Early nasolabial fold development",
                "texture_coarseness": "Generally smooth with minor texture",
                "pigment_spots": "Few age spots, mild photoaging",
                "redness_erythema": "Even tone, no significant redness",
                "pore_visibility": "Moderately visible pores",
                "sebum_shine": "Normal to dry sebum levels",
                "hydration_dryness": "Good hydration status"
            }
        },
        "skin_conditions": {
            "acne": "No active acne lesions present",
            "pigmentation": "Mild age spots on cheeks and forehead, consistent with photoaging",
            "texture": "Overall smooth with minor roughness in T-zone",
            "pores": "Moderately visible throughout face, consistent with age",
            "sebum": "Normal to low sebum production, balanced complexion",
            "wrinkles": "Dynamic and static lines present, moderate for age group",
            "redness": "Minimal erythema, even skin tone overall",
            "dark_circles": "Mild under-eye darkness, possibly vascular and pigmentary"
        },
        "aging_signs": {
            "sagging": "Early jawline softening, minimal jowling",
            "elasticity_loss": "Mild loss of elasticity in periorbital and cheek areas",
            "photoaging_cues": "Sun damage evident through pigmentation and texture changes"
        },
        "quality_assessment": {
            "lighting": "Good natural lighting, even distribution",
            "blur": "No motion blur, adequate sharpness",
            "occlusions": "No significant occlusions from hair or accessories",
            "angle": "Frontal view optimal for analysis",
            "makeup_filters": "Minimal makeup, no apparent digital filters",
            "color_cast": "Natural color balance, no significant tinting"
        }
    }
    
    print("✅ LLaVA analysis complete - Pure visual observations recorded")
    return findings

def stage2_medgemma_medical_interpretation(llava_findings: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Stage 2: MedGemma Medical Interpretation (CALCULATION & MEDICAL TEXT)
    
    Model: MedGemma (local)
    Role: Ingest LLaVA's observations + optional user metadata and:
        (a) compute all scores, severities, and skin age
        (b) assign classifications (e.g., Glogau)
        (c) generate human Markdown report AND strict JSON
    """
    
    print("\n🏥 STAGE 2: MedGemma Medical Interpretation")
    print("=" * 50)
    print("Processing LLaVA findings with MedGemma...")
    print(f"User metadata: {metadata or 'None provided'}")
    
    # Simulate MedGemma processing time
    time.sleep(3)
    
    # Generate the exact markdown report format from the prompt
    chronological_age = metadata.get('chronological_age') if metadata else None
    delta_text = f" (Δ +4 years vs chronological age)" if chronological_age else ""
    
    markdown_report = f"""## 📋 Two-Stage Medical AI Pipeline
**Stage 1**: LLaVA Clinical Vision Analysis
**Stage 2**: MedGemma Medical Interpretation
**Processing**: Sequential Medical AI for Consistent Results

## 👁️ Clinical Vision Findings:

**A) Age Estimation:** {llava_findings['age_estimation']}

**B) Zone Analysis:** Comprehensive evaluation across facial zones reveals moderate photoaging consistent with chronological age range.

**C) Skin Conditions:** {llava_findings['skin_conditions']['pigmentation']}. {llava_findings['skin_conditions']['texture']}. {llava_findings['skin_conditions']['wrinkles']}.

**D) Aging Signs:** {llava_findings['aging_signs']['sagging']}. {llava_findings['aging_signs']['elasticity_loss']}.

**E) Quality Assessment:** {llava_findings['quality_assessment']['lighting']}. {llava_findings['quality_assessment']['makeup_filters']}.

## 🏥 Medical Interpretation:

### 1. Dermatological Diagnosis with Severity Grading (0–4 Scale)
- **Mild photoaging** - Severity: 2
- **Fine lines and wrinkles** - Severity: 2  
- **Age-related pigmentation** - Severity: 1
- **Mild elasticity loss** - Severity: 1

### 2. Precise Skin Age Estimation (years)
**Skin Age: 42 years**{delta_text}

### 3. Glogau Photoaging Classification (I–IV)
**Type II** - Wrinkles in motion, early brown spots. Justification: Dynamic lines present with early pigmentary changes.

### 4. Acne Grading if Present
**N/A** - No active acne lesions observed.

### 5. Treatment Recommendations (evidence-aligned, OTC-first)

**Topicals:**
- Retinol 0.25-0.5% (start 2x/week, build to nightly)
- Vitamin C serum 10-15% (morning application)  
- Niacinamide 5-10% (AM/PM)
- Alpha hydroxy acids 5-10% (2-3x/week)

**Sun Protection:**
- Broad-spectrum SPF 50+ daily
- Reapplication every 2 hours during sun exposure

**Routines:**
- **AM:** Gentle cleanser → Vitamin C → Niacinamide → Moisturizer → SPF
- **PM:** Double cleanse → Retinol (alternate nights) → Moisturizer
- **Weekly:** AHA treatment (1-2x)

**In-clinic options:**
- Chemical peels (glycolic 20-30%)
- Microneedling with PRP
- IPL for pigmentation
- Radiofrequency for skin tightening

**Timelines:**
- Short (2-6w): Improved hydration and texture
- Medium (8-16w): Visible reduction in fine lines and pigmentation  
- Long (4-12m): Significant improvement in skin quality and aging markers

### 6. Red Flags Requiring Referral
- Any new or changing pigmented lesions
- Persistent irritation or inflammation
- Suspected skin cancer signs

### 7. Important Considerations / Disclaimers
This analysis is for educational purposes only and does not constitute medical diagnosis. Professional dermatological consultation is recommended for personalized treatment planning and monitoring.

## 📊 Clinical Summary:
- **Skin Age:** 42 years
- **Glogau Type:** II  
- **Top 3 concerns:** Photoaging, fine lines, pigmentation
- **Pipeline:** LLaVA → MedGemma

## ⚠️ Medical Disclaimer:
This educational analysis does not constitute medical diagnosis or treatment advice. Consult a licensed dermatologist for professional evaluation and personalized care recommendations."""

    # Generate the strict JSON format from the prompt
    structured_data = {
        "usable": True,
        "quality_notes": ["Good lighting conditions", "Minimal occlusions", "Adequate image resolution"],
        "views_received": {"frontal": True, "left_profile": False, "right_profile": False},
        "zones_visible": ["forehead", "temple_left", "temple_right", "periorbital", "nose", "cheek_left", "cheek_right", "perioral", "chin", "jawline_left", "jawline_right", "neck"],
        "skin_condition": {
            "acne": {"severity_0_4": 0, "marker_0_100": 5, "confidence_0_100": 95, "zones": []},
            "pigmentation": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 85, "zones": ["cheek_left", "cheek_right", "forehead"]},
            "redness": {"severity_0_4": 0, "marker_0_100": 10, "confidence_0_100": 90, "zones": []},
            "texture": {"severity_0_4": 1, "marker_0_100": 20, "confidence_0_100": 80, "zones": ["forehead", "nose"]},
            "pores": {"severity_0_4": 2, "marker_0_100": 40, "confidence_0_100": 85, "zones": ["nose", "cheek_left", "cheek_right"]},
            "sebum": {"severity_0_4": 1, "marker_0_100": 30, "confidence_0_100": 75, "zones": ["forehead", "nose"]},
            "barrier": {"severity_0_4": 0, "marker_0_100": 15, "confidence_0_100": 70},
            "hydration": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 75},
            "dark_circles": {"severity_0_4": 1, "marker_0_100": 30, "confidence_0_100": 80}
        },
        "aging": {
            "skin_age_years": 42,
            "chronological_age_years": chronological_age,
            "delta_years": 42 - chronological_age if chronological_age else None,
            "glogau_type": "II",
            "wrinkles": {"severity_0_4": 2, "marker_0_100": 45, "confidence_0_100": 85, "zones": ["crow_feet", "forehead_lines", "nasolabial"]},
            "sagging": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 75, "zones": ["jawline"]}
        },
        "lifestyle": {
            "stress_markers": {"severity_0_4": 1, "marker_0_100": 20, "confidence_0_100": 60},
            "screen_fatigue": {"severity_0_4": 1, "marker_0_100": 30, "confidence_0_100": 65},
            "lip_health": {"severity_0_4": 0, "marker_0_100": 10, "confidence_0_100": 70},
            "smoking_damage": {"severity_0_4": 0, "marker_0_100": 5, "confidence_0_100": 80},
            "sleep_deficit": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 60}
        },
        "hormonal_cues": {
            "hormonal_acne": {"present": False, "severity_0_4": 0, "confidence_0_100": 90, "notes": "No hormonal acne patterns observed"},
            "pcos_thyroid": {"suggestive": False, "confidence_0_100": 85, "notes": "No clear endocrine markers visible"},
            "nutrient_def": {"suggestive": False, "confidence_0_100": 75, "notes": "No obvious nutritional deficiency signs"}
        },
        "environmental_damage": {
            "uv_damage": {"severity_0_4": 2, "marker_0_100": 40, "confidence_0_100": 85},
            "pollution": {"severity_0_4": 1, "marker_0_100": 20, "confidence_0_100": 70},
            "oxidative": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 75},
            "thermal_flushing": {"severity_0_4": 0, "marker_0_100": 10, "confidence_0_100": 80}
        },
        "referral_flags": [],
        "care_plan": {
            "morning": [
                "Gentle cleanser with lukewarm water",
                "Vitamin C serum 10-15%", 
                "Niacinamide 5-10%",
                "Lightweight moisturizer",
                "Broad-spectrum SPF 50+"
            ],
            "night": [
                "Double cleanse (oil cleanser + gentle foam)",
                "Retinol 0.25-0.5% (alternate nights)",
                "Hydrating moisturizer",
                "Facial oil if needed for extra moisture"
            ],
            "weekly": [
                "AHA treatment 5-10% (2x per week)",
                "Hydrating mask (1x per week)",
                "Gentle facial massage for circulation"
            ]
        }
    }
    
    print("✅ MedGemma interpretation complete - Medical analysis and recommendations generated")
    
    return {
        "markdown_report": markdown_report,
        "structured_data": structured_data
    }

def execute_dermaging_pipeline():
    """
    Execute the complete DermAging Two-Stage pipeline
    """
    
    print("🧬 DermAging Two-Stage Medical AI Pipeline")
    print("=" * 60)
    print("Sequential processing: LLaVA → MedGemma")
    print("Processing: Sequential Medical AI for Consistent Results\n")
    
    # Sample input data
    image_paths = {
        "frontal": "sample_face_frontal.jpg",
        "left_profile": None,
        "right_profile": None
    }
    
    user_metadata = {
        "chronological_age": 38,
        "sex": "F",
        "skin_type": "combo"
    }
    
    start_time = time.time()
    
    # Stage 1: LLaVA Clinical Vision Analysis
    stage1_findings = stage1_llava_clinical_vision_analysis(image_paths, user_metadata)
    
    # Stage 2: MedGemma Medical Interpretation  
    stage2_result = stage2_medgemma_medical_interpretation(stage1_findings, user_metadata)
    
    processing_time = time.time() - start_time
    
    # Final output
    print(f"\n📊 PIPELINE COMPLETE")
    print("=" * 50)
    print(f"⏱️  Total processing time: {processing_time:.2f} seconds")
    print(f"🎯 Pipeline version: 1.0.0")
    print(f"🧠 Models used: LLaVA (vision) → MedGemma (medical)")
    
    print(f"\n📋 MARKDOWN REPORT:")
    print("-" * 30)
    print(stage2_result["markdown_report"])
    
    print(f"\n📊 STRUCTURED JSON DATA:")
    print("-" * 30)
    print(json.dumps(stage2_result["structured_data"], indent=2))
    
    return {
        "stage1_findings": stage1_findings,
        "stage2_interpretation": stage2_result,
        "processing_time": processing_time,
        "pipeline_version": "1.0.0"
    }

if __name__ == "__main__":
    result = execute_dermaging_pipeline() 