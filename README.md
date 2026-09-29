# AI Virality Predictor

An AI-powered video analytics and prediction system built with **Python, Flask, OpenCV, scikit-learn, and SQLite**.

The system analyzes an uploaded video, extracts visual and temporal features, predicts its potential performance using a machine learning model, generates recommendations, stores analysis history, and can generate a PDF report.

> **Note:** The current project is a working prototype. Prediction quality depends on the size and quality of the available training dataset.

---

## Features

### 1. Video Upload

Upload a video through the Flask web interface.

The system accepts a video and performs automated analysis.

### 2. Video Feature Extraction

The application extracts features including:

* Video duration
* FPS
* Resolution
* Motion score
* Scene changes
* Hook intensity
* Face count
* Face presence ratio
* Brightness
* Contrast
* Pacing score

### 3. Machine Learning Prediction

The extracted features are passed to a trained machine learning model.

The system produces:

* Virality score
* Estimated views
* Prediction result

The current trained model is stored using Joblib.

### 4. Recommendations

The recommendation module analyzes the extracted features and provides suggestions such as:

* Improving the first few seconds of the video
* Increasing or reducing motion
* Improving pacing
* Improving visual characteristics
* Optimizing audience engagement characteristics

### 5. Analysis History

Previous video analyses are stored in SQLite.

The history page allows previously generated analysis results to be viewed.

### 6. PDF Report Generation

The application can generate a PDF report containing the video analysis and prediction information.

### 7. Video Thumbnail

A representative thumbnail is generated from the uploaded video and displayed on the result page.

---

# Technology Stack

| Technology   | Purpose                              |
| ------------ | ------------------------------------ |
| Python       | Core programming language            |
| Flask        | Web application framework            |
| OpenCV       | Video processing and computer vision |
| NumPy        | Numerical processing                 |
| Pandas       | Dataset processing                   |
| scikit-learn | Machine learning                     |
| Joblib       | Model persistence                    |
| SQLite       | Analysis history database            |
| ReportLab    | PDF report generation                |
| HTML         | Frontend structure                   |
| CSS          | Frontend styling                     |
| JavaScript   | Frontend interactions                |

---

# Project Structure

```text
ai_virality_predictor/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
│   ├── config.py
│   └── __init__.py
│
├── data/
│   ├── dataset_manifest.csv
│   ├── training_data.csv
│   ├── README.md
│   └── videos/
│
├── database/
│   ├── database.py
│   ├── schema.sql
│   └── __init__.py
│
├── ml/
│   ├── features.py
│   ├── predict.py
│   ├── preprocessing.py
│   ├── train.py
│   └── __init__.py
│
├── models/
│   ├── virality_model.joblib
│   └── virality_scaler.joblib
│
├── recommendations/
│   ├── recommender.py
│   └── __init__.py
│
├── reports/
│   ├── report_generator.py
│   └── generated/
│
├── scripts/
│   └── build_training_dataset.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── thumbnails/
│
├── templates/
│   ├── index.html
│   ├── result.html
│   └── history.html
│
├── uploads/
│
└── utils/
    ├── helpers.py
    └── __init__.py
```

---

# Requirements

Recommended Python version:

```text
Python 3.10+
```

The project dependencies are listed in:

```text
requirements.txt
```

---

# Installation

## 1. Clone the repository

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project:

```powershell
cd ai_virality_predictor
```

---

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(venv)
```

---

## 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

If a dependency needs to be installed separately:

```powershell
python -m pip install flask
```

For PDF report generation:

```powershell
python -m pip install reportlab
```

---

# Running the Application

Make sure the virtual environment is activated.

From the project root:

```powershell
python app.py
```

The Flask server should start on:

```text
http://127.0.0.1:5000
```

Open the address in a browser.

---

# Video Analysis Workflow

The application follows this workflow:

```text
Upload Video
      ↓
Video Validation
      ↓
Feature Extraction
      ↓
Machine Learning Prediction
      ↓
Virality Score
      ↓
Estimated Views
      ↓
Recommendations
      ↓
Save Analysis History
      ↓
Generate PDF Report
```

---

# Extracted Video Features

The current system extracts the following features.

## Duration

Length of the uploaded video in seconds.

## FPS

Frames per second of the video.

## Resolution

Video width and height.

## Motion Score

Measures the amount of visual movement between frames.

Higher movement can indicate more dynamic visual content.

## Scene Changes

Estimates the number of major visual scene transitions.

## Hook Intensity

A feature intended to represent the visual intensity of the opening portion of the video.

The first few seconds are important for viewer retention.

## Face Count

Detects faces in sampled video frames.

> Face detection is currently based on computer-vision detection and may occasionally produce false positives.

## Face Presence Ratio

Percentage of sampled frames containing detected faces.

## Brightness

Measures the average brightness of sampled frames.

## Contrast

Measures the visual contrast of the video.

## Pacing Score

Represents the temporal/visual pacing characteristics of the video.

---

# Machine Learning

The project uses a machine learning model to estimate video performance.

The model uses extracted video features as input.

The prediction pipeline is approximately:

```text
Video
  ↓
Feature Extraction
  ↓
Feature Vector
  ↓
Preprocessing / Scaling
  ↓
ML Model
  ↓
Estimated Views
  ↓
Virality Score
```

The trained model files are:

```text
models/virality_model.joblib
models/virality_scaler.joblib
```

---

# Training Dataset

Training data is maintained under:

```text
data/
```

Important files include:

```text
data/dataset_manifest.csv
data/training_data.csv
```

Training videos are stored under:

```text
data/videos/
```

The dataset manifest contains the video information and target performance values used for model development.

---

# Building the Training Dataset

The project contains:

```text
scripts/build_training_dataset.py
```

Run:

```powershell
python scripts/build_training_dataset.py
```

This processes the available training videos and prepares feature data.

The generated feature file is:

```text
video_features.csv
```

---

# Training the Model

After preparing the training data, run:

```powershell
python -m ml.train
```

Depending on the current training implementation, the trained model files will be saved under:

```text
models/
```

Expected model files include:

```text
virality_model.joblib
virality_scaler.joblib
```

---

# Running Prediction

Prediction functionality is implemented in:

```text
ml/predict.py
```

The application uses the trained model when available.

The prediction output includes:

```text
Virality Score
Estimated Views
```

---

# Important Dataset Limitation

The current prototype has a relatively small training dataset.

Because machine learning models require sufficient representative training data, predictions from a small dataset should be treated as **experimental estimates rather than guaranteed real-world view counts**.

For better performance, the project should eventually be trained using a much larger dataset containing:

* More videos
* More creators/channels
* Multiple content categories
* Actual views
* Likes
* Comments
* Shares
* Publication information
* Video-level features

---

# SQLite Database

Analysis history is stored using SQLite.

Database-related files are located under:

```text
database/
```

The database schema is defined in:

```text
database/schema.sql
```

The local database file is:

```text
database/virality.db
```

The database stores analysis history generated by the application.

---

# PDF Reports

PDF report generation is implemented in:

```text
reports/report_generator.py
```

Generated reports are stored locally under:

```text
reports/generated/
```

Reports are intentionally excluded from GitHub because they are generated output files.

---

# Thumbnails

Generated thumbnails are stored under:

```text
static/thumbnails/
```

These are generated during video analysis and are excluded from Git tracking except for the `.gitkeep` file.

---

# Uploaded Videos

Uploaded videos are temporarily stored under:

```text
uploads/
```

Uploaded videos should not be committed to GitHub because video files can be very large and may contain user-provided content.

---

# GitHub Setup

## Initialize Git

From the project root:

```powershell
git init
```

Check the repository:

```powershell
git status
```

---

## Add files

After checking `.gitignore`:

```powershell
git add .
```

Check what will be committed:

```powershell
git status
```

Make the first commit:

```powershell
git commit -m "Initial commit - AI Virality Predictor"
```

---

## Set main branch

```powershell
git branch -M main
```

---

## Connect GitHub repository

Replace the URL with your actual GitHub repository URL:

```powershell
git remote add origin YOUR_GITHUB_REPOSITORY_URL
```

Check:

```powershell
git remote -v
```

---

## Push to GitHub

```powershell
git push -u origin main
```

---

# Future Updates

After making changes:

```powershell
git status
git add .
git commit -m "Update AI Virality Predictor"
git push
```

---

# Important Files Not Committed to GitHub

The following generated or local files should normally remain outside GitHub:

```text
venv/
__pycache__/
uploads/*.mp4
static/thumbnails/*.jpg
reports/generated/*.pdf
database/virality.db
video_features.csv
*.joblib
*.pkl
```

The `.gitignore` file is used to prevent these files from being accidentally committed.

---

# Troubleshooting

## Flask not found

Run:

```powershell
python -m pip install flask
```

---

## ReportLab not found

Run:

```powershell
python -m pip install reportlab
```

---

## Check Python version

```powershell
python --version
```

---

## Check installed packages

```powershell
pip list
```

---

## Check Flask application

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Model not found

Check:

```text
models/
```

Expected files:

```text
virality_model.joblib
virality_scaler.joblib
```

If the model has not been trained, run the model-training process first.

---

## Dataset problems

Check:

```text
data/dataset_manifest.csv
data/training_data.csv
```

Make sure the dataset contains valid numeric target values and valid video paths.

---

# Current Project Status

The current prototype supports:

* Video upload
* Video feature extraction
* Computer vision analysis
* ML-based prediction
* Virality score
* Estimated views
* Recommendations
* SQLite history
* Thumbnail generation
* PDF report generation
* Flask web interface

The project is currently under active development.

---

# Future Improvements

Potential future improvements include:

* Larger and more diverse training dataset
* Better face detection
* Improved scene detection
* Audio feature extraction
* Speech analysis
* Sentiment analysis
* OCR/text extraction
* Object detection
* Better hook analysis
* Social-media-specific prediction models
* More advanced recommendation system
* Model evaluation dashboard
* Cross-validation and model comparison
* Creator/category-specific predictions
* Deployment to a production server

---

# Disclaimer

This project is intended for experimentation, research, and demonstration of video analytics and machine-learning techniques.

The generated virality score and estimated views are model-based estimates and should not be interpreted as guaranteed future performance.
