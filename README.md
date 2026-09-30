<div align="center">

# REALEYES

### Deepfake detection for face images, built on a custom CNN.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-1f2937?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-1f2937?style=flat-square&logo=tensorflow&logoColor=white)
![API](https://img.shields.io/badge/API-FastAPI%20%7C%20Flask-1f2937?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-1f2937?style=flat-square)

[Overview](#overview) · [Architecture](#system-architecture) · [Workflow](#end-to-end-workflow) · [Model](#model-specification) · [Training](#training-pipeline) · [API](#api-reference) · [Quick Start](#quick-start) · [Roadmap](#roadmap)

</div>

---

## Overview

Synthetic media is now cheap to produce and hard to spot by eye. It drives misinformation, identity fraud, and social engineering at scale.

**RealEyes** is an end-to-end pipeline that classifies a face image as **Real** or **Fake**. It combines a purpose-built convolutional network with a strict preprocessing stage and a lightweight inference API. The result is a system that is easy to run locally and easy to extend into a larger forensics stack.

| Principle | What it means in practice |
|---|---|
| **Simple** | One command to run locally. No cluster, no GPU required for inference. |
| **Modular** | Preprocessing, model, and serving layers are independent and replaceable. |
| **Measurable** | Every prediction returns a calibrated confidence score, not just a label. |
| **Extensible** | Designed to grow toward video, temporal models (LSTM/GRU), and cloud hosting. |

---

## Capabilities

**Detection**
- Binary Real / Fake classification with a confidence score
- Trained on face-swap, GAN-generated, and blended-region manipulations
- Automatic preprocessing, so callers send raw images
- Regularised with dropout and augmentation to generalise to unseen data

**Serving**
- Image upload interface for fast manual testing
- Backend prediction API with structured logging and error handling
- Portable `.keras` model artifact, ready for REST or cloud deployment

---

## System Architecture

```mermaid
flowchart LR
    subgraph CLIENT["Client Layer"]
        UI["Web UI<br/>HTML / CSS / JS"]
        EXT["External Client<br/>cURL / SDK"]
    end

    subgraph API["Service Layer"]
        GW["Prediction API<br/>FastAPI / Flask"]
        VAL["Request Validation<br/>type, size, integrity"]
    end

    subgraph CORE["Inference Core"]
        PRE["Preprocessing<br/>decode, resize, normalise"]
        MODEL["Custom CNN<br/>.keras artifact"]
        POST["Post-processing<br/>threshold, confidence"]
    end

    subgraph OPS["Observability"]
        LOG["Structured Logs"]
        ERR["Error Handling"]
    end

    UI --> GW
    EXT --> GW
    GW --> VAL
    VAL --> PRE
    PRE --> MODEL
    MODEL --> POST
    POST --> GW
    GW -.-> LOG
    VAL -.-> ERR
    MODEL -.-> LOG
```

Each layer has a single responsibility. The model can be swapped, the API framework changed, or the frontend replaced without touching the other layers.

---

## End-to-End Workflow

The full lifecycle runs from raw data to a served prediction, in two connected loops: **training** (offline) and **inference** (online).

```mermaid
flowchart TD
    A["Raw Dataset<br/>real + deepfake images"] --> B["Data Validation<br/>corrupt files, class balance"]
    B --> C["Face Alignment<br/>optional"]
    C --> D["Resize to 224x224"]
    D --> E["Normalise Pixel Values"]
    E --> F["Train / Validation Split"]

    F --> G["Augmentation<br/>flip, jitter, noise, zoom"]
    G --> H["Cached Batch Pipeline"]
    H --> I["CNN Training<br/>Adam + Binary Cross-Entropy"]
    I --> J{"Validation loss<br/>improving?"}
    J -- "Yes" --> I
    J -- "No, patience reached" --> K["Early Stopping"]
    K --> L["Evaluation<br/>held-out test set"]
    L --> M{"Meets<br/>release criteria?"}
    M -- "No" --> N["Tune data, architecture,<br/>or hyperparameters"]
    N --> G
    M -- "Yes" --> O["Export .keras Model"]

    O --> P["Model Registry / Repo"]
    P --> Q["Inference Service"]

    R["User Upload"] --> S["Validate Input"]
    S --> T["Preprocess<br/>same transforms as training"]
    T --> Q
    Q --> U["Real / Fake<br/>+ Confidence"]
```

> **Training / serving parity.** The inference path applies the same resize and normalisation as training. Any mismatch between the two is a common cause of silent accuracy loss, so keep the transforms in one shared module.

### Inference sequence

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as API
    participant P as Preprocessor
    participant M as CNN Model

    C->>A: POST /predict (image)
    A->>A: Validate type, size, integrity
    alt Invalid input
        A-->>C: 4xx with error detail
    else Valid input
        A->>P: Raw image bytes
        P->>P: Decode, resize 224x224, normalise
        P->>M: Tensor (1, 224, 224, 3)
        M-->>A: Probability score
        A->>A: Apply threshold, format response
        A-->>C: label + confidence
    end
```

---

## Model Specification

| Component | Detail |
|---|---|
| Framework | TensorFlow / Keras |
| Architecture | Custom CNN |
| Input | 224 × 224 RGB |
| Output | Single sigmoid unit: probability of *Fake* |
| Loss | Binary Cross-Entropy |
| Optimiser | Adam |
| Regularisation | Dropout, data augmentation, early stopping |
| Artifact | `.keras` |

```mermaid
flowchart LR
    IN["Input<br/>224x224x3"] --> C1["Conv Block 1"]
    C1 --> C2["Conv Block 2"]
    C2 --> C3["Conv Block N"]
    C3 --> FL["Flatten / Global Pool"]
    FL --> D1["Dense"]
    D1 --> DO["Dropout"]
    DO --> OUT["Sigmoid<br/>P(Fake)"]
```

> Replace the block counts and layer sizes above with the exact configuration from your training notebook.

### Training data

A balanced set of real and manipulated face images covering three manipulation families:

| Family | Description |
|---|---|
| Face-swap | Identity from one subject transplanted onto another |
| GAN-generated | Fully synthetic faces with no real source |
| Blended regions | Local facial edits composited into a genuine image |

---

## Training Pipeline

| Stage | Steps |
|---|---|
| **1. Preparation** | Load dataset, optional face alignment, resize, normalise |
| **2. Augmentation** | Random horizontal flip, brightness and contrast jitter, noise injection, slight random zoom |
| **3. Training** | Batched training with efficient caching, validation monitoring, early stopping |
| **4. Evaluation** | Held-out test set, confusion matrix, per-manipulation breakdown |
| **5. Export** | Save `.keras` artifact and version it alongside its preprocessing config |

### Reported performance

Fill this table from your final evaluation run.

| Metric | Value |
|---|---|
| Accuracy | — |
| Precision (Fake) | — |
| Recall (Fake) | — |
| F1 score | — |
| ROC-AUC | — |

---

## Detection Signals

Generative models leave measurable traces. The network is trained to pick up on low-level patterns that are hard for a human to notice.

| Signal | Cause |
|---|---|
| **Texture inconsistency** | GANs struggle to reproduce natural skin micro-texture uniformly. |
| **Boundary artifacts** | Blending seams where a replacement face meets the original frame. |
| **Lighting mismatch** | Shadow direction and specular highlights that disagree across the face. |
| **Eye and teeth distortion** | Fine structures that generators often render with subtle errors. |

---

## API Reference

> Endpoint names below are the recommended contract. Adjust them to match your backend.

### `POST /predict`

Classify a single image.

**Request**

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@sample.jpg"
```

**Response `200`**

```json
{
  "label": "fake",
  "confidence": 0.9312,
  "model_version": "1.0.0",
  "inference_ms": 48
}
```

**Errors**

| Code | Meaning |
|---|---|
| `400` | Missing file or unreadable image |
| `413` | File exceeds the size limit |
| `415` | Unsupported media type |
| `500` | Inference failure, see server logs |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<your-username>/RealEyes.git
cd RealEyes

# 2. Create an isolated environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the service
python app.py                    # or: uvicorn app:app --reload
```

Open `http://localhost:8000`, upload an image, and read the verdict.

### Suggested project layout

```text
RealEyes/
├── model/            # trained .keras artifact
├── src/
│   ├── preprocess.py # shared transforms (training + inference)
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
├── api/              # service layer
├── frontend/         # minimal upload UI
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Machine learning | TensorFlow, Keras |
| Backend | Python, FastAPI or Flask |
| Frontend | HTML, CSS, JavaScript |
| Utilities | NumPy, Pillow, OpenCV |

---

## Limitations

A detector is a probabilistic tool, not proof. Read these before relying on it.

- **Distribution shift.** Performance can drop on manipulation methods absent from the training data. New generators appear constantly.
- **Image quality.** Heavy compression, low resolution, and re-uploads can erase the artifacts the model depends on.
- **Not a legal verdict.** Treat the confidence score as one signal in a wider review process, especially for high-stakes decisions.
- **Adversarial inputs.** A determined attacker can craft images designed to evade detection.

---

## Roadmap

```mermaid
flowchart LR
    NOW["Current<br/>Image classification<br/>CNN + API"] --> N1["Next<br/>Threshold calibration<br/>Model versioning"]
    N1 --> N2["Then<br/>Video detection<br/>frame sampling"]
    N2 --> N3["Later<br/>Temporal models<br/>LSTM / GRU"]
    N3 --> N4["Scale<br/>Containerised deploy<br/>Cloud model hosting"]
```

- [x] Custom CNN classifier with confidence output
- [x] Preprocessing pipeline and upload interface
- [ ] Explainability maps (Grad-CAM) to show *why* an image was flagged
- [ ] Video pipeline with frame-level aggregation
- [ ] Docker image and CI for tests and linting
- [ ] Public benchmark results across multiple datasets

---

## Contributing

Issues and pull requests are welcome. For larger changes, open an issue first so the approach can be discussed.

1. Fork the repository
2. Create a feature branch
3. Commit with clear messages
4. Open a pull request describing what changed and why

---

## Author

**Aayush Shukla**

---

<div align="center">

If RealEyes is useful to you, consider starring the repository. It helps others find it.

</div>
