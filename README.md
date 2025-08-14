# 🧬 **DermAging Two-Stage Medical AI Pipeline**

> **Advanced Dermatological Analysis System with Real AI Models**

A production-ready medical AI system that combines **LLaVA computer vision** and **MedGemma medical intelligence** to provide comprehensive dermatological analysis, aging assessment, and personalized skincare recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)

## 🎯 **Overview**

DermAging AI is a **two-stage medical pipeline** that provides professional-grade dermatological analysis:

1. **🔍 Stage 1 - LLaVA Clinical Vision**: Computer vision analysis of facial images
2. **🏥 Stage 2 - MedGemma Medical Intelligence**: Medical interpretation and scoring

**✨ Key Features:**
- 🧠 **Real AI Models**: LLaVA + MedGemma (no mock data)
- 🎨 **Production UI**: Beautiful dark theme with real-time progress
- 📊 **Comprehensive Analysis**: 15+ skin condition assessments
- 🎯 **Personalized Care**: Morning, evening, and weekly routines
- ⚡ **Optimized Performance**: Smart timeout handling and error recovery
- 🛡️ **Medical Grade**: Professional scoring and safety disclaimers

---

## 🌟 **Demo & Screenshots**

### **Main Interface**
Beautiful dark theme with three-tab navigation:
- **Upload & Configure**: Drag-and-drop image upload + patient metadata
- **AI Analysis**: Real-time progress with stage indicators
- **Results & Report**: Comprehensive dermatological analysis

### **Analysis Features**
- **Skin Age Assessment**: Biological vs chronological age comparison
- **Glogau Classification**: Type I-IV photoaging assessment  
- **Severity Scoring**: 0-4 scale for 15+ skin conditions
- **Environmental Damage**: UV, pollution, oxidative stress analysis
- **Lifestyle Impact**: Stress markers, sleep quality, screen fatigue
- **Care Plans**: Evidence-based morning/evening/weekly routines

---

## 🚀 **Quick Start**

### **Prerequisites**
- **Node.js** 18+ 
- **Python** 3.8+
- **Ollama** (for local AI models)

### **1. Clone Repository**
```bash
git clone <repository-url>
cd dermaging-ai
```

### **2. Install Dependencies**
```bash
# Frontend dependencies
npm install

# Python dependencies  
pip install -r requirements.txt
```

### **3. Set Up AI Models**
```bash
# Install LLaVA model
ollama pull llava:latest

# Install MedGemma model
ollama pull amsaravi/medgemma-4b-it:q8
```

### **4. Start Services**
```bash
# Terminal 1: Start LLaVA server
python llava-server.py

# Terminal 2: Start MedGemma server  
python medgemma-server.py

# Terminal 3: Start Next.js frontend
npm run dev
```

### **5. Access Application**
Open [http://localhost:3000](http://localhost:3000) in your browser

---

## 🛠️ **Architecture**

### **Tech Stack**
```
Frontend:
├── Next.js 14 (App Router)
├── TypeScript
├── TailwindCSS + shadcn/ui
├── Zustand (State Management)
├── Zod (Validation)
└── React Hot Toast

Backend:
├── Python Flask (AI Servers)
├── Ollama (Local AI Hosting)
├── LLaVA (Computer Vision)
└── MedGemma (Medical Intelligence)
```

### **System Flow**
```
1. User uploads facial image + metadata
2. Frontend → Next.js API → LLaVA Server
3. LLaVA analyzes image (vision-only)
4. Findings → MedGemma Server  
5. MedGemma provides medical interpretation
6. Results → Frontend display
```

### **File Structure**
```
dermaging-ai/
├── src/
│   ├── app/
│   │   ├── api/analyze/route.ts     # Main analysis pipeline
│   │   ├── page.tsx                 # Main UI component
│   │   └── layout.tsx               # App layout
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   └── providers.tsx            # React providers
│   ├── store/
│   │   └── analysisStore.ts         # Zustand state management
│   └── types/
│       └── dermaging.ts             # TypeScript definitions
├── llava-server.py                  # LLaVA AI server
├── medgemma-server.py               # MedGemma AI server
└── README.md
```

---

## 🎮 **Usage Guide**

### **Step 1: Upload Image**
- Drag & drop or click to upload facial image
- Supported formats: JPEG, PNG, WebP (max 10MB)
- Clear frontal view recommended

### **Step 2: Add Patient Info (Optional)**
- **Age**: For age comparison analysis
- **Sex**: For hormonal factor assessment  
- **Skin Type**: Fitzpatrick I-VI classification

### **Step 3: Start Analysis**
- Click "Start AI Analysis"
- Watch real-time progress (2-4 minutes total)
- Automatic navigation through stages

### **Step 4: Review Results**
- **Key Metrics**: Skin age, Glogau type, confidence scores
- **Detailed Analysis**: 15+ skin condition assessments
- **Personalized Care**: Morning/evening/weekly routines
- **Medical Report**: Comprehensive markdown report

---

## 📊 **Analysis Output**

### **Skin Condition Metrics** (0-4 Scale)
- **Acne Severity**: Inflammatory lesion assessment
- **Pigmentation**: Age spots, discoloration analysis
- **Texture Quality**: Surface smoothness evaluation
- **Pore Visibility**: Sebaceous activity scoring
- **Wrinkle Formation**: Fine line and fold assessment

### **Aging Assessment**
- **Skin Age**: Biological age estimation (years)
- **Glogau Classification**: Type I-IV photoaging
- **Age Delta**: Difference vs chronological age
- **Confidence Metrics**: Analysis reliability scores

### **Environmental Damage**
- **UV Damage**: Photoaging marker assessment
- **Pollution Impact**: Environmental stress indicators
- **Oxidative Stress**: Free radical damage analysis

### **Personalized Care Plans**
- **Morning Routine**: SPF, antioxidants, hydration
- **Evening Routine**: Retinol, AHA, moisturizing
- **Weekly Treatments**: Masks, exfoliation, massage

---

## ⚙️ **Configuration**

### **Environment Variables**
```env
# Optional: Custom AI model endpoints
LLAVA_ENDPOINT=http://localhost:8001
MEDGEMMA_ENDPOINT=http://localhost:8002
```

### **Performance Tuning**
```python
# llava-server.py optimizations
max_size = 512          # Image resize limit
quality = 75            # JPEG compression
timeout = 300           # Request timeout (seconds)
num_predict = 800       # Model prediction tokens
num_ctx = 2048          # Context window size

# medgemma-server.py optimizations  
timeout = 120           # Reduced timeout
num_predict = 400       # Faster prediction
num_ctx = 1024          # Smaller context
num_thread = 4          # CPU thread limit
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Frontend not loading**
```bash
# Check port conflicts
lsof -i :3000
# Restart frontend
npm run dev
```

**2. AI models timeout**
```bash
# Check Ollama status
ollama list
# Restart Ollama
ollama serve
```

**3. Analysis fails**
```bash
# Check server health
curl http://localhost:8001/health
curl http://localhost:8002/health
# Restart servers
python llava-server.py
python medgemma-server.py
```

**4. Memory issues**
- Reduce image size (< 5MB recommended)
- Close other applications
- Restart AI servers

### **Performance Optimization**
- **Images**: Use clear, well-lit frontal photos
- **Hardware**: 8GB+ RAM recommended for AI models
- **Network**: Local processing (no internet required)

---

## 🛡️ **Medical Disclaimer**

⚠️ **Important Notice**: This system is for **educational and informational purposes only**. 

**Not a substitute for professional medical advice:**
- Results are AI-generated assessments
- Not intended for medical diagnosis
- Consult healthcare professionals for medical concerns
- Do not use for emergency medical situations

**Professional consultation recommended for:**
- Persistent skin conditions
- Unusual lesions or changes
- Severe acne or inflammation
- Suspected skin cancer or pathology

---

## 🤝 **Contributing**

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly  
5. **Submit** a pull request

### **Development Setup**
```bash
# Install dev dependencies
npm install --include=dev
pip install -r requirements-dev.txt

# Run tests
npm run test
python -m pytest

# Type checking
npm run type-check
mypy *.py
```

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **LLaVA**: Large Language and Vision Assistant
- **MedGemma**: Medical AI from Google DeepMind
- **Ollama**: Local AI model hosting
- **Next.js**: React framework
- **shadcn/ui**: Beautiful UI components

---

## 📞 **Support**

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Documentation**: [Wiki](../../wiki)

---

**🎯 Ready to analyze skin health with professional-grade AI? Get started now!**

```bash
git clone <repository-url>
cd dermaging-ai
npm install && pip install -r requirements.txt
ollama pull llava:latest && ollama pull amsaravi/medgemma-4b-it:q8
```

**👉 [Start Your Analysis](http://localhost:3000) ←** 