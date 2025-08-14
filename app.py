from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from health_score import HealthScoreCalculator
import json
import logging
import uvicorn
import os
from starlette.responses import RedirectResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)
TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "index.html")

# Write the HTML template to the templates directory if not present
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Score Calculator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-5">
    <h1 class="mb-4">Health Score Calculator</h1>
    <form method="post">
        <div class="mb-3">
            <label for="json_data" class="form-label">Paste your health data JSON here:</label>
            <textarea class="form-control" id="json_data" name="json_data" rows="10">{{ example_json }}</textarea>
        </div>
        <button type="submit" class="btn btn-primary">Calculate</button>
    </form>
    {% if error %}
    <div class="alert alert-danger mt-3">{{ error }}</div>
    {% endif %}
    {% if score is not none %}
    <hr>
    <h2>Overall Health Assessment</h2>
    <table class="table table-bordered w-auto">
        <tr><th>Overall Health Score</th><th>Assessment</th></tr>
        <tr><td>{{ '%.1f' % score }}%</td><td>{{ assessment }}</td></tr>
    </table>
    <h3>System-wise Breakdown</h3>
    <table class="table table-bordered w-auto">
        <tr><th>System</th><th>Score</th><th>Status</th></tr>
        {% for system in system_scores %}
        <tr>
            <td>{{ system.name }}</td>
            <td>{{ '%.1f' % system.score }}%</td>
            <td>{{ system.status }}</td>
        </tr>
        {% endfor %}
    </table>
    <h3>Detailed Biomarker Analysis</h3>
    <table class="table table-bordered w-auto">
        <tr><th>System</th><th>Organ</th><th>Biomarker</th><th>Score</th><th>Status</th></tr>
        {% for b in biomarker_details %}
        <tr>
            <td>{{ b.system }}</td>
            <td>{{ b.organ }}</td>
            <td>{{ b.biomarker }}</td>
            <td>{{ '%.1f' % b.score }}%</td>
            <td>{{ b.status }}</td>
        </tr>
        {% endfor %}
    </table>
    <h3>Imputed Biomarker Values</h3>
    {% if imputed_values %}
    <table class="table table-bordered w-auto">
        <tr><th>Biomarker</th><th>Imputed Value</th></tr>
        {% for imp in imputed_values %}
        <tr><td>{{ imp.biomarker }}</td><td>{{ imp.value }}</td></tr>
        {% endfor %}
    </table>
    {% endif %}
    <h3>Predicted 5-Year Risk (Cox Regression)</h3>
    {% if risk is not none %}
    <div class="alert alert-info">Predicted 5-year risk: <b>{{ (risk*100)|round(1) }}%</b></div>
    {% endif %}
    {% endif %}
</div>
</body>
</html>
'''
if not os.path.exists(TEMPLATE_PATH):
    with open(TEMPLATE_PATH, "w") as f:
        f.write(HTML_TEMPLATE)

templates = Jinja2Templates(directory=TEMPLATES_DIR)

calculator = HealthScoreCalculator()

EXAMPLE_JSON = json.dumps({
    "phr_id": "5e42d90dd905bd98d723eec3",
    "age": 36.0,
    "gender": "Male",
    "biomarkers": [
        {"loinc_id": "2885-2", "value": 7.6, "report_unit": "g/dL"},
        {"loinc_id": "2571-8", "value": 84.0, "report_unit": "mg/dL"},
        {"loinc_id": "2093-3", "value": 147.0, "report_unit": "mg/dL"},
        {"loinc_id": "6299-2", "value": 8.88, "report_unit": "mg/dL"},
        {"loinc_id": "1975-2", "value": 0.6, "report_unit": "mg/dL"},
        {"loinc_id": "2091-7", "value": 16.8, "report_unit": "mg/dL"},
        {"loinc_id": "1971-1", "value": 0.3, "report_unit": "mg/dL"},
        {"loinc_id": "2085-9", "value": 39.0, "report_unit": "mg/dL"}
    ],
    "age_bucket": "18-39"
}, indent=2)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "example_json": EXAMPLE_JSON,
        "score": None,
        "assessment": None,
        "system_scores": [],
        "biomarker_details": [],
        "imputed_values": [],
        "risk": None,
        "error": None
    })

@app.post("/", response_class=HTMLResponse)
async def post_index(request: Request):
    form = await request.form()
    json_data = form.get("json_data", "").strip()
    logger.info(f"Received POST request with data: {json_data[:100]}...")
    score = None
    assessment = None
    system_scores = []
    biomarker_details = []
    imputed_values = []
    risk = None
    error = None
    try:
        data = json.loads(json_data)
        score_val, system_scores_dict, biomarker_values = calculator.calculate_score_from_data(data)
        assessment = calculator.get_health_assessment(score_val)
        score = score_val
        # Prepare system-wise breakdown
        for system_name, system_data in system_scores_dict.items():
            system_score = system_data['score'] * 100
            status = "Good" if system_score >= 70 else "Needs Attention"
            system_scores.append({
                'name': system_name.title(),
                'score': system_score,
                'status': status
            })
            for organ_name, organ_data in system_data['organs'].items():
                for biomarker_name, biomarker_score in organ_data['biomarkers'].items():
                    b_score = biomarker_score * 100
                    b_status = "Good" if b_score >= 70 else "Needs Attention"
                    biomarker_details.append({
                        'system': system_name.title(),
                        'organ': organ_name.title(),
                        'biomarker': biomarker_name.replace('_', ' ').title(),
                        'score': b_score,
                        'status': b_status
                    })
        # Show imputed values
        input_biomarkers = set([b['loinc_id'] for b in data['biomarkers']])
        for biomarker, value in biomarker_values.items():
            if biomarker not in [b['loinc_id'] for b in data['biomarkers']]:
                imputed_values.append({
                    'biomarker': biomarker.replace('_', ' ').title(),
                    'value': value
                })
        # Predict future risk
        risk = calculator.predict_future_risk({
            **biomarker_values,
            'age': data.get('age', 50)
        })
        logger.info(f"Successfully processed request. Score: {score_val}")
    except json.JSONDecodeError as e:
        error = f"Invalid JSON format: {str(e)}"
        logger.error(f"JSON decode error: {str(e)}")
    except Exception as e:
        error = f"Error processing input: {str(e)}"
        logger.error(f"Processing error: {str(e)}")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "example_json": EXAMPLE_JSON,
        "score": score,
        "assessment": assessment,
        "system_scores": system_scores,
        "biomarker_details": biomarker_details,
        "imputed_values": imputed_values,
        "risk": risk,
        "error": error
    })

@app.post("/api/score", response_class=JSONResponse)
async def api_score(request: Request):
    try:
        data = await request.json()
        score_val, system_scores_dict, biomarker_values = calculator.calculate_score_from_data(data)
        assessment = calculator.get_health_assessment(score_val)
        # Prepare system-wise breakdown
        system_scores = []
        biomarker_details = []
        for system_name, system_data in system_scores_dict.items():
            system_score = system_data['score'] * 100
            status = "Good" if system_score >= 70 else "Needs Attention"
            system_scores.append({
                'name': system_name.title(),
                'score': system_score,
                'status': status
            })
            for organ_name, organ_data in system_data['organs'].items():
                for biomarker_name, biomarker_score in organ_data['biomarkers'].items():
                    b_score = biomarker_score * 100
                    b_status = "Good" if b_score >= 70 else "Needs Attention"
                    biomarker_details.append({
                        'system': system_name.title(),
                        'organ': organ_name.title(),
                        'biomarker': biomarker_name.replace('_', ' ').title(),
                        'score': b_score,
                        'status': b_status
                    })
        # Show imputed values
        imputed_values = []
        input_biomarkers = set([b['loinc_id'] for b in data['biomarkers']])
        for biomarker, value in biomarker_values.items():
            if biomarker not in [b['loinc_id'] for b in data['biomarkers']]:
                imputed_values.append({
                    'biomarker': biomarker.replace('_', ' ').title(),
                    'value': value
                })
        # Predict future risk
        risk = calculator.predict_future_risk({
            **biomarker_values,
            'age': data.get('age', 50)
        })
        return JSONResponse({
            "score": score_val,
            "assessment": assessment,
            "system_scores": system_scores,
            "biomarker_details": biomarker_details,
            "imputed_values": imputed_values,
            "risk": risk
        })
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/report", response_class=HTMLResponse)
async def report(request: Request, phr_id: str = None):
    # For demo, use the same test data as before
    # In production, fetch user data by phr_id from DB
    test_data = {
        "phr_id": "1361cc6cf45541b2a94f3c4eaf228703",
        "age": 34.8,
        "gender": "Male",
        "biomarkers": [
            {"loinc_id": "2089-1", "value": 134.73, "report_unit": "value"},
            {"loinc_id": "2085-9", "value": 90.42, "report_unit": "value"},
            {"loinc_id": "2093-3", "value": 233.64, "report_unit": "value"},
            {"loinc_id": "2571-8", "value": 38.76, "report_unit": "value"},
            {"loinc_id": "1884-6", "value": 134.98, "report_unit": "value"},
            {"loinc_id": "1869-7", "value": 90.0, "report_unit": "value"},
            {"loinc_id": "1874-7", "value": 0.79, "report_unit": "value"},
            {"loinc_id": "30522-7", "value": 0.25, "report_unit": "value"},
            {"loinc_id": "13965-9", "value": 21.59, "report_unit": "value"},
            {"loinc_id": "10835-7", "value": 24.45, "report_unit": "value"},
            {"loinc_id": "2160-0", "value": 0.57, "report_unit": "value"},
            {"loinc_id": "69405-9", "value": 31.57, "report_unit": "value"},
            {"loinc_id": "6299-2", "value": 24.27, "report_unit": "value"},
            {"loinc_id": "32294-1", "value": 14.2, "report_unit": "value"},
            {"loinc_id": "3084-1", "value": 0.95, "report_unit": "value"},
            {"loinc_id": "14957-5", "value": 2.29, "report_unit": "value"},
            {"loinc_id": "1920-8", "value": 45.69, "report_unit": "value"},
            {"loinc_id": "1742-6", "value": 49.71, "report_unit": "value"},
            {"loinc_id": "2324-2", "value": 35.2, "report_unit": "value"},
            {"loinc_id": "1968-7", "value": 9.34, "report_unit": "value"},
            {"loinc_id": "1971-1", "value": 0.32, "report_unit": "value"},
            {"loinc_id": "1975-2", "value": 1.18, "report_unit": "value"},
            {"loinc_id": "1751-7", "value": 4.79, "report_unit": "value"},
            {"loinc_id": "2885-2", "value": 6.21, "report_unit": "value"},
            {"loinc_id": "6768-6", "value": 126.33, "report_unit": "value"},
            {"loinc_id": "3016-3", "value": 0.09, "report_unit": "value"},
            {"loinc_id": "3053-6", "value": 181.03, "report_unit": "value"},
            {"loinc_id": "3026-2", "value": 96.64, "report_unit": "value"},
            {"loinc_id": "17861-6", "value": 10.73, "report_unit": "value"},
            {"loinc_id": "49045-0", "value": 121.15, "report_unit": "value"},
            {"loinc_id": "2132-9", "value": 768.22, "report_unit": "value"},
            {"loinc_id": "718-7", "value": 11.03, "report_unit": "value"},
            {"loinc_id": "26453-1", "value": 2.23, "report_unit": "value"},
            {"loinc_id": "6690-2", "value": 64.25, "report_unit": "value"},
            {"loinc_id": "13056-7", "value": 383.65, "report_unit": "value"},
            {"loinc_id": "2498-4", "value": 199.16, "report_unit": "value"},
            {"loinc_id": "3024-7", "value": 288.36, "report_unit": "value"},
            {"loinc_id": "20567-4", "value": 336.51, "report_unit": "value"},
            {"loinc_id": "2593-2", "value": 37.06, "report_unit": "value"},
            {"loinc_id": "2951-2", "value": 148.97, "report_unit": "value"},
            {"loinc_id": "6298-4", "value": 0.43, "report_unit": "value"},
            {"loinc_id": "24519-1", "value": 3.4, "report_unit": "value"},
            {"loinc_id": "1558-6", "value": 122.19, "report_unit": "value"},
            {"loinc_id": "4548-4", "value": 7.46, "report_unit": "value"},
            {"loinc_id": "33043-1", "value": "not present", "report_unit": "value"},
            {"loinc_id": "50555-2", "value": "not present", "report_unit": "value"}
        ],
        "age_bucket": "18-39"
    }
    calculator = HealthScoreCalculator()
    score, system_scores, biomarker_values, explanations = calculator.calculate_score_from_data(test_data, explain=True)
    assessment = calculator.get_health_assessment(score)
    return templates.TemplateResponse("report.html", {
        "request": request,
        "score": score,
        "assessment": assessment,
        "system_scores": system_scores,
        "explanations": explanations,
        "biomarker_values": biomarker_values,
        "user": test_data
    })

# If not present, create a basic report.html template
report_template_path = os.path.join("templates", "report.html")
if not os.path.exists(report_template_path):
    with open(report_template_path, "w") as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Health Score Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1, h2, h3 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; }
        .good { color: green; }
        .attention { color: red; }
        .explanation { font-size: 0.95em; color: #555; }
    </style>
</head>
<body>
    <h1>Health Score Report</h1>
    <h2>User: {{ user.gender }} Age: {{ user.age }}</h2>
    <h2>Overall Health Score: <span class="{{ 'good' if score >= 70 else 'attention' }}">{{ '%.1f' % score }}%</span> ({{ assessment }})</h2>
    <h3>System-wise Breakdown</h3>
    <table>
        <tr>
            <th>System</th>
            <th>Score</th>
        </tr>
        {% for system, sdata in system_scores.items() %}
        <tr>
            <td>{{ system.title() }}</td>
            <td><span class="{{ 'good' if sdata.score*100 >= 70 else 'attention' }}">{{ '%.1f' % (sdata.score*100) }}%</span></td>
        </tr>
        {% endfor %}
    </table>
    <h3>Detailed Biomarker Analysis</h3>
    {% for system, sdata in system_scores.items() %}
        <h4>{{ system.title() }}</h4>
        {% for organ, odata in sdata.organs.items() %}
            <b>{{ organ.title() }}</b>
            <table>
                <tr>
                    <th>Biomarker</th>
                    <th>Value</th>
                    <th>Normal Range</th>
                    <th>Optimal Range</th>
                    <th>Score</th>
                    <th>Explanations</th>
                </tr>
                {% for biomarker, score in odata.biomarkers.items() %}
                <tr>
                    <td>{{ biomarker.replace('_', ' ').title() }}</td>
                    <td>{{ explanations[system][organ][biomarker].value }}</td>
                    <td>{{ explanations[system][organ][biomarker].normal_range }}</td>
                    <td>{{ explanations[system][organ][biomarker].optimal_range }}</td>
                    <td><span class="{{ 'good' if score*100 >= 70 else 'attention' }}">{{ '%.1f' % (score*100) }}%</span></td>
                    <td class="explanation">
                        {% for note in explanations[system][organ][biomarker].notes %}
                            • {{ note }}<br>
                        {% endfor %}
                        {% if explanations[system][organ][biomarker].risk_factors %}
                            <b>Risk Factors:</b><br>
                            {% for k, v in explanations[system][organ][biomarker].risk_factors.items() %}
                                - {{ k }}: {{ v }}<br>
                            {% endfor %}
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        {% endfor %}
    {% endfor %}
</body>
</html>
''')

if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True) 