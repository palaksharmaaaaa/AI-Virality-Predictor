# 🎯 AI Virality Predictor

An AI-powered video analytics and virality prediction system that analyzes uploaded videos using **Computer Vision, Machine Learning, Audio Analysis, Speech Transcription, Content Analysis, and Creator/Platform insights**.

The system extracts meaningful video features such as motion, scene changes, hook intensity, human presence, visible faces, brightness, contrast, pacing, audio/speech characteristics, and transcript-based content signals to estimate the video's potential performance.

---

## 🚀 Features

### 🎥 Video Analysis

The system analyzes uploaded videos and extracts:

* Video duration
* FPS
* Resolution
* Aspect ratio
* Video format
* File size
* Brightness
* Contrast
* Motion score
* Scene changes
* Scene change rate
* Pacing score
* Hook intensity
* Person count
* Person presence ratio
* Visible face count
* Face presence ratio
* Number of sampled frames

### 🤖 AI-Based Person Detection

The project uses:

**SSDLite320 MobileNetV3-Large**

with pretrained COCO weights from the PyTorch/Torchvision ecosystem.

The detector is used to identify people in video frames.

Pipeline:

```text
Video Frame
     ↓
SSDLite320 MobileNetV3-Large
     ↓
Person Detection
     ↓
Person Bounding Boxes
     ↓
Head/Upper Region Analysis
     ↓
Face Verification
     ↓
Person Count + Visible Face Count
```

The system keeps person detection separate from face detection because a person may be visible even when their face is not visible, for example in:

* Top-down camera views
* Back-facing people
* Side-facing people
* Occluded people
* Crowded scenes

---

## 🎙️ Audio & Speech Analysis

The system extracts audio from the uploaded video using **FFmpeg**.

Audio analysis includes:

* Audio availability
* Speech ratio
* Silence ratio
* Music/activity ratio

For speech transcription, the project uses:

**Qwen3-ASR**

Model:

```text
Qwen/Qwen3-ASR-0.6B-hf
```

The transcription pipeline supports multilingual speech and can produce transcripts containing English, Hindi, Hinglish, and other supported languages.

---

## 📝 Transcript & Content Analysis

The transcript is analyzed to extract content-related signals such as:

* Word count
* Unique words
* Character count
* Sentence count
* Vocabulary diversity
* Filler word ratio
* Hook score
* CTA detection
* CTA score
* Question count
* Sentiment
* Sentiment score
* Keywords
* Speech density
* Transcript quality

The content analyzer is designed to handle Unicode text so that Hindi and other non-ASCII scripts are not incorrectly treated as empty text.

Example:

```text
आज हम लोग एक important topic के बारे में बात करेंगे।
अगर आपको यह वीडियो अच्छा लगे तो like और share जरूर करें।
```

can be analyzed instead of returning zero word counts.

---

## 🧠 Machine Learning

The project uses a machine-learning regression model to estimate video performance.

Current model:

```text
RandomForestRegressor
```

The model uses extracted video and related analytical features to generate:

* Virality Score
* Estimated Views / Reach

Example:

```text
Virality Score: 20 / 100
Estimated Views: 278,349
```

> The prediction is an ML estimate based on the available training data. It should not be interpreted as a guaranteed number of views.

---

## 📊 Prediction Pipeline

```text
                Uploaded Video
                      │
                      ▼
              Video Processing
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Visual Analysis  Audio        Metadata
        │          Analysis          │
        ▼             ▼             ▼
 Motion / Scenes   Speech /       Duration /
 Faces / People    Silence        FPS / Size
        │             │
        └─────────────┼─────────────┘
                      ▼
              Feature Engineering
                      │
                      ▼
             Machine Learning Model
                      │
                      ▼
              Virality Prediction
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Virality Score             Estimated Views
```

---

## 🌐 Web Application

The application is built using:

* Python
* Flask
* HTML
* CSS
* JavaScript

Flask provides the backend and routing, while HTML/CSS/JavaScript provide the user interface.

---

## 🗄️ Database

The project uses:

**SQLite**

The database stores analysis information and historical predictions.

The application provides an analysis history so previously processed videos can be reviewed.

---

## 📄 Generated Reports

The application can generate detailed PDF reports containing analysis results.

Reports can include:

* Video information
* Visual features
* Audio information
* Transcript/content analysis
* Virality prediction
* Recommendations

PDF reports are generated using **ReportLab**.

---

## 📁 Project Structure

```text
AI-Virality-Predictor/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
│   ├── __init__.py
│   └── config.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── schema.sql
│
├── video/
│   ├── __init__.py
│   ├── extractor.py
│   ├── transcript.py
│   └── thumbnail.py
│
├── content/
│   ├── __init__.py
│   └── content_analyzer.py
│
├── creator/
│   ├── __init__.py
│   └── creator_analyzer.py
│
├── platform_analysis/
│   ├── __init__.py
│   └── platform_analyzer.py
│
├── hashtag/
│   ├── __init__.py
│   └── hashtag_analyzer.py
│
├── ml/
│   ├── __init__.py
│   ├── train.py
│   └── predict.py
│
├── models/
│   ├── virality_model.joblib
│   └── virality_scaler.joblib
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── history.html
│
├── static/
│   └── css/
│       └── style.css
│
├── data/
│   └── ...
│
├── reports/
│   └── ...
│
└── uploads/
    └── ...
```

---

## 🛠️ Technologies Used

| Technology          | Purpose                              |
| ------------------- | ------------------------------------ |
| Python              | Core programming language            |
| Flask               | Web application backend              |
| OpenCV              | Video processing and computer vision |
| NumPy               | Numerical processing                 |
| PyTorch             | Deep learning framework              |
| Torchvision         | SSDLite object detection             |
| Pillow              | Image processing                     |
| Scikit-learn        | Machine learning                     |
| Qwen3-ASR           | Speech-to-text transcription         |
| FFmpeg              | Audio/video processing               |
| SQLite              | Database                             |
| ReportLab           | PDF report generation                |
| HTML/CSS/JavaScript | Frontend                             |

---

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/palaksharmaaaaa/AI-Virality-Predictor.git
```

Move into the project directory:

```bash
cd AI-Virality-Predictor
```

---

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

---

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

If PyTorch and Torchvision are not included in `requirements.txt`, install them separately:

```powershell
pip install torch torchvision pillow
```

Install FFmpeg separately and make sure it is available in the system PATH.

Verify:

```powershell
ffmpeg -version
```

---

## ▶️ Run the Application

After activating the virtual environment:

```powershell
python app.py
```

The Flask application will start locally.

Open:

```text
http://127.0.0.1:5000
```

in your browser.

---

## 📤 Using the Application

### Step 1

Open the application in your browser.

### Step 2

Upload a video.

### Step 3

The system extracts video features.

### Step 4

Audio is extracted and transcribed when speech is available.

### Step 5

The transcript is analyzed for content characteristics.

### Step 6

The machine-learning model generates the virality prediction.

### Step 7

The result page displays:

```text
Video Analysis
      ↓
Audio Analysis
      ↓
Content & Transcript
      ↓
Creator Analysis
      ↓
Platform Analysis
      ↓
Hashtag Analysis
      ↓
Virality Prediction
      ↓
Recommendations
```

---

## 📈 Example Output

Example video analysis:

```text
Duration              : 37.40 sec
FPS                   : 29.97
Resolution            : 1280x720
Brightness            : 109.82
Contrast              : 62.50
Motion Score          : 5.10
Scene Changes         : 0
Person Count          : 3
Face Count            : 0
Hook Intensity        : 30.20
Pacing Score          : 0.00
```

Example prediction:

```text
Virality Score        : 20 / 100
Estimated Views       : 278,349
Model                 : RandomForestRegressor
```

The exact output depends on the uploaded video and the trained model.

---

## 🧪 Model Training

The machine-learning training pipeline is located in:

```text
ml/train.py
```

Prediction logic is located in:

```text
ml/predict.py
```

The trained model is stored in:

```text
models/
```

Before deploying or presenting the project as a production prediction system, the model should be trained using a sufficiently large and representative dataset.

---

## 🔍 Feature Engineering

The current video feature set includes:

```text
duration
fps
width
height
motion_score
scene_changes
scene_change_rate
face_count
face_presence_ratio
brightness
contrast
hook_intensity
pacing_score
```

Additional content/audio features can be combined with the visual features to improve the prediction pipeline.

---

## ⚠️ Limitations

The system has several practical limitations:

1. Virality cannot be guaranteed from video features alone.
2. Prediction quality depends heavily on the quality and size of the training dataset.
3. Person detection and face detection are different tasks.
4. Small, occluded, back-facing, or extreme-angle faces may not be detected.
5. CPU inference can be slower than GPU inference.
6. Estimated views are model predictions, not guaranteed platform metrics.
7. Social-media algorithms change over time and vary between platforms.

---

## 🔮 Future Improvements

Potential improvements include:

* Larger real-world training dataset
* Better target-variable engineering
* Dedicated neural face detector
* Crowd/person tracking across frames
* Object detection and scene understanding
* Better hook detection
* Multilingual NLP
* Advanced sentiment analysis
* Transformer-based transcript analysis
* Platform-specific prediction models
* YouTube/Instagram/TikTok analytics integration
* Model explainability
* Prediction confidence intervals
* Continuous model retraining
* GPU acceleration
* Real-time video analysis

---

## 🔐 Privacy

Uploaded videos may contain personal or sensitive information.

For production deployment:

* Secure uploaded files
* Limit file size
* Validate file types
* Delete temporary files when processing is complete
* Avoid storing unnecessary user data
* Protect database access
* Add authentication where required

---

## 👩‍💻 Author

**Palak Sharma**

B.Tech — Artificial Intelligence & Machine Learning

---

## 📌 Project

**AI Virality Predictor – Video Analytics and Prediction System**

Built with Python, Flask, Computer Vision, NLP/ASR, and Machine Learning.
