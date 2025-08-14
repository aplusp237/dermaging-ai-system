# 🤖 DermAging Model Setup Guide

This guide will help you connect your local LLaVA and MedGemma models to the DermAging Two-Stage pipeline.

## 📋 Required Model Endpoints

The DermAging system expects these local endpoints to be running:

- **LLaVA Vision Model**: `http://localhost:8001/analyze`
- **MedGemma Medical Model**: `http://localhost:8002/interpret`

## 🔧 LLaVA Model Setup (Port 8001)

### Expected API Format:

**Endpoint**: `POST http://localhost:8001/analyze`

**Request**: FormData containing images
```javascript
// FormData structure
frontal: File          // Required - frontal face image
left_profile: File     // Optional - left profile image  
right_profile: File    // Optional - right profile image
```

**Response**: JSON matching ClinicalVisionFindings interface
```json
{
  "age_estimation": "late 30s–early 40s",
  "zone_analysis": {
    "forehead": {
      "fine_lines_wrinkles": "Visual observation text",
      "texture_coarseness": "Visual observation text",
      "pigment_spots": "Visual observation text",
      "redness_erythema": "Visual observation text",
      "pore_visibility": "Visual observation text", 
      "sebum_shine": "Visual observation text",
      "hydration_dryness": "Visual observation text"
    },
    // ... other facial zones (temple_left, temple_right, periorbital, nose, etc.)
  },
  "skin_conditions": {
    "acne": "Visual observation text",
    "pigmentation": "Visual observation text",
    "texture": "Visual observation text",
    "pores": "Visual observation text",
    "sebum": "Visual observation text",
    "wrinkles": "Visual observation text",
    "redness": "Visual observation text",
    "dark_circles": "Visual observation text"
  },
  "aging_signs": {
    "sagging": "Visual observation text",
    "elasticity_loss": "Visual observation text", 
    "photoaging_cues": "Visual observation text"
  },
  "quality_assessment": {
    "lighting": "Visual observation text",
    "blur": "Visual observation text",
    "occlusions": "Visual observation text",
    "angle": "Visual observation text",
    "makeup_filters": "Visual observation text",
    "color_cast": "Visual observation text"
  }
}
```

### Sample LLaVA Server (Python Flask):

```python
from flask import Flask, request, jsonify
import base64
from PIL import Image
import io

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_images():
    try:
        # Get uploaded images
        frontal = request.files.get('frontal')
        left_profile = request.files.get('left_profile')
        right_profile = request.files.get('right_profile')
        
        if not frontal:
            return jsonify({"error": "Frontal image required"}), 400
            
        # Process images with your LLaVA model here
        # ... your LLaVA processing logic ...
        
        # Return clinical vision findings
        return jsonify({
            "age_estimation": "late 30s–early 40s",
            "zone_analysis": {
                # Your zone analysis results
            },
            "skin_conditions": {
                # Your skin condition observations
            },
            "aging_signs": {
                # Your aging sign observations  
            },
            "quality_assessment": {
                # Your quality assessment
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
```

## 🏥 MedGemma Model Setup (Port 8002)

### Expected API Format:

**Endpoint**: `POST http://localhost:8002/interpret`

**Request**: JSON containing LLaVA findings + metadata
```json
{
  "llava_findings": {
    // Complete LLaVA response from Stage 1
  },
  "user_metadata": {
    "chronological_age": 38,
    "sex": "F", 
    "skin_type": "combo"
  }
}
```

**Response**: JSON with markdown report + structured data
```json
{
  "markdown_report": "## 📋 Two-Stage Medical AI Pipeline...",
  "structured_data": {
    "usable": true,
    "quality_notes": ["Good lighting conditions"],
    "views_received": {"frontal": true, "left_profile": false, "right_profile": false},
    "zones_visible": ["forehead", "temple_left", ...],
    "skin_condition": {
      "acne": {"severity_0_4": 0, "marker_0_100": 5, "confidence_0_100": 95, "zones": []},
      // ... other conditions
    },
    "aging": {
      "skin_age_years": 42,
      "chronological_age_years": 38,
      "delta_years": 4,
      "glogau_type": "II",
      "wrinkles": {"severity_0_4": 2, "marker_0_100": 45, "confidence_0_100": 85, "zones": ["crow_feet"]},
      "sagging": {"severity_0_4": 1, "marker_0_100": 25, "confidence_0_100": 75, "zones": ["jawline"]}
    },
    "lifestyle": {
      // Lifestyle markers with severity/confidence scores
    },
    "hormonal_cues": {
      // Hormonal analysis
    },
    "environmental_damage": {
      // Environmental damage assessment
    },
    "referral_flags": [],
    "care_plan": {
      "morning": ["Step 1", "Step 2", ...],
      "night": ["Step 1", "Step 2", ...], 
      "weekly": ["Step 1", ...]
    }
  }
}
```

### Sample MedGemma Server (Python Flask):

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/interpret', methods=['POST'])
def interpret_findings():
    try:
        data = request.get_json()
        llava_findings = data.get('llava_findings')
        user_metadata = data.get('user_metadata', {})
        
        if not llava_findings:
            return jsonify({"error": "LLaVA findings required"}), 400
            
        # Process with your MedGemma model here
        # ... your MedGemma processing logic ...
        
        # Generate markdown report
        markdown_report = generate_medical_report(llava_findings, user_metadata)
        
        # Generate structured data  
        structured_data = generate_structured_analysis(llava_findings, user_metadata)
        
        return jsonify({
            "markdown_report": markdown_report,
            "structured_data": structured_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
```

## 🚀 Quick Start Commands

### 1. Start LLaVA Model Server (Terminal 1):
```bash
cd /path/to/your/llava/model
python llava_server.py  # Should start on port 8001
```

### 2. Start MedGemma Model Server (Terminal 2):
```bash
cd /path/to/your/medgemma/model  
python medgemma_server.py  # Should start on port 8002
```

### 3. Verify Models Are Running:
```bash
# Test LLaVA endpoint
curl -I http://localhost:8001/analyze

# Test MedGemma endpoint  
curl -I http://localhost:8002/interpret
```

### 4. Start DermAging Frontend (Terminal 3):
```bash
cd /path/to/dermaging-two-stage
npm run dev  # Already running on http://localhost:3001
```

## 🔍 Testing the Pipeline

1. **Check Model Status**: The DermAging interface will show if models are connected
2. **Upload Test Image**: Use a clear frontal face photo
3. **Monitor Console**: Check browser dev tools and server logs for connection status
4. **Fallback Behavior**: If models aren't available, the system uses mock data with warnings

## 🛠️ Troubleshooting

### Common Issues:

**Port Already in Use**:
```bash
# Kill process on port 8001 or 8002
lsof -ti:8001 | xargs kill -9
lsof -ti:8002 | xargs kill -9
```

**CORS Issues**:
Add CORS headers to your Flask servers:
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

**Image Format Issues**:
Ensure your models accept common formats (JPEG, PNG, WebP)

**Response Format Errors**:
Check that your model responses exactly match the expected JSON schemas

## 📊 Integration Status

- ✅ **Next.js Frontend**: Running on http://localhost:3001
- ⏳ **LLaVA Model**: Connect to http://localhost:8001/analyze
- ⏳ **MedGemma Model**: Connect to http://localhost:8002/interpret
- ✅ **Fallback System**: Mock data if models unavailable
- ✅ **Error Handling**: Graceful degradation and user feedback

Once both models are running, the DermAging system will automatically use them instead of mock data! 