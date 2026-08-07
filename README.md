# SAI Algorithm — DDoS Detection 


*A lightweight, high-accuracy algorithm to detect real DDoS attacks using repeated time-gap patterns between packets.*

Live notebook: [https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing](https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing)

---

## Overview

SAI is a purpose-built algorithm that detects Distributed Denial of Service (DDoS) attacks by finding repeated, nearly-equal inter-packet time gaps from the same source IP — a common signature of automated/bot traffic. The method focuses on a minimal set of features (source IP, timestamp / inter-arrival time pattern) and achieves very high accuracy with low computational overhead.

---

## Table of Contents

* [What is a DDoS attack?](#what-is-a-ddos-attack)
* [Why detection is hard](#why-detection-is-hard)
* [SAI approach (high level)](#sai-approach-high-level)
* [Repo / Notebook contents](#repo--notebook-contents)
* [Environment & dependencies](#environment--dependencies)
* [Quick start (run in Colab)](#quick-start-run-in-colab)
* [Run locally (optional)](#run-locally-optional)
* [How to use SAI for real-world prevention](#how-to-use-sai-for-real-world-prevention)
* [Model comparison & results](#model-comparison--results)
* [Evaluation metrics](#evaluation-metrics)
* [Troubleshooting & tips](#troubleshooting--tips)
* [License & contact](#license--contact)

---

## What is a DDoS attack?

A Distributed Denial of Service (DDoS) attack floods a target (server, API, network) with a large volume of traffic coming from multiple sources to exhaust resources and make the service unavailable to legitimate users. Attack sources may be compromised machines (botnets) or coordinated scripts.

---

## Why detection is hard

* Attack traffic often mimics legitimate traffic patterns (variable payloads, randomized headers).
* High-volume legitimate spikes (e.g., marketing campaign) can appear similar to an attack.
* Signature-based detectors fail when attackers change packet-level signatures.
* Real-time analysis at scale requires low-latency processing and feature selection.
* Many attacks use multiple IPs, making per-IP thresholds insufficient.

---

## SAI approach (high level)

1. **Feature focus:** Track per-source-IP inter-packet time gaps (∆t = timestamp_i - timestamp_{i-1}).
2. **Pattern detection:** Look for repeated/equivalent ∆t values across consecutive packets from the same IP within a sliding window.
3. **Scoring:** Compute a pattern score (e.g., variance or frequency of repeated ∆t). Low variance + high repetition → suspicious.
4. **Decision:** If the pattern score exceeds a threshold, classify as attack traffic. Optionally combine with lightweight additional signals (packet size constancy, TCP flags) for improved robustness.
5. **Action:** Raise alerts, throttle or block IP(s), or hand off to mitigation infra (rate-limiter, WAF, CDN).

> Rationale: Automated attack tools often send packets at near-constant intervals. Detecting this temporal regularity is computationally cheap and highly discriminative.

---

## Repo / Notebook contents

The shared Colab notebook contains:

* Data loading and preprocessing (time-based sorting, per-IP grouping)
* Feature extraction (inter-arrival times, repetition counts, statistical features)
* Implementation of baseline models (KNN, RandomForest, SVM, Neural Net, Gradient Boosting, Decision Tree)
* Implementation & training of the **SAI Algorithm**
* Model evaluation and comparison (accuracy, confusion matrix, other metrics)
* Export of trained model and simple inference examples

Link: [https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing](https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing)

---

## Environment & dependencies

Below is a representative list — use the notebook `requirements` cell (if available) or add these to `requirements.txt`.

```text
python>=3.8
pandas
numpy
scikit-learn
xgboost
tensorflow   # if Neural Network implemented with TF/Keras
joblib       # model save/load
matplotlib   # plots
```

Install (locally) example:

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Quick start (run in Colab)

1. Open the notebook:
   [https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing](https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing)
2. Runtime → Change runtime type → GPU (optional).
3. Run cells in order. The notebook contains cells that:

   * mount Google Drive (if needed)
   * download/load the dataset (or instruction to upload)
   * train baselines and SAI
   * compute metrics and display the comparison table
4. To reproduce `SAI Algorithm` accuracy, ensure the same preprocessing and random seeds are used (notebook sets them).

---

## Run locally (optional)

Use the same notebook code as `.py` scripts. Example minimal inference flow:

```python
import pandas as pd
import joblib
from sai_detector import SaiDetector  # if implemented as class

# load model
model = joblib.load('sai_model.pkl')

# prepare a small batch of incoming packets as dataframe with columns: ['src_ip','timestamp','...']
df = pd.read_csv('incoming_flow_sample.csv')
predictions = model.predict(df)  # or model.predict_proba / detector.score(df)
```

---

## How to use SAI for real-world prevention

1. **Streaming input:** integrate SAI into the traffic pipeline (edge proxy, load balancer, IDS). Use a sliding time window per source IP.
2. **Windowing:** maintain a fixed-size ring buffer of the last N timestamps for each source IP. Compute inter-arrival times on insertion and update pattern score incrementally.
3. **Thresholding & smoothing:** use a configurable threshold + exponential smoothing to avoid false positives during short bursts.
4. **Mitigation actions:** when SAI flags an IP:

   * apply progressive throttling (e.g., limit connections or requests per second), or
   * temporarily block IP for a short window, or
   * redirect suspicious traffic to a CAPTCHA / challenge page, or
   * escalate to WAF/CDN with more aggressive mitigation rules.
5. **Deploy at edge:** run SAI at CDN edge or load-balancer level for early detection and minimal latency.
6. **Logging & feedback loop:** store flagged flows to retrain and tune thresholds; combine with other telemetry (geolocation, ASN, payload patterns) for adaptive rules.

---

## Model comparison & results

Results reported in the notebook (baseline vs SAI):

| Model                  |  Accuracy (%) |
| ---------------------- | ------------: |
| KNeighbors             |     89.315317 |
| RandomForest           |     88.889127 |
| Support Vector Machine |     89.528413 |
| Neural Network         |     89.651534 |
| Gradient Boosting      |     90.456561 |
| Decision Tree          |     89.509471 |
| **SAI Algorithm**      | **99.890000** |

> Notes: These numbers reflect the dataset, preprocessing, feature engineering, and train/test split used in the notebook. Reproducibility requires identical preprocessing and seeds.

---

## Evaluation metrics

Beyond Accuracy, evaluate using:

* Precision, Recall, F1-score (important when class imbalance exists)
* Confusion matrix (TP, FP, TN, FN)
* ROC-AUC and PR-AUC (for probabilistic outputs)
* Detection latency (time from first malicious packet to detection)
* Throughput / CPU usage (to verify real-time suitability)

---

## Reproducing the 99.89% accuracy

To get similar results:

1. Use the same dataset and same train/test split.
2. Apply identical preprocessing: per-IP ordering, sliding-window size, thresholding for "same time gap" equivalence (e.g., tolerance ε ms).
3. Ensure feature pipeline (e.g., counts of repeated ∆t, mean ∆t, ∆t variance) matches notebook.
4. Use same model hyperparameters and random seed. The notebook contains the exact code/hyperparams.

---

## Practical considerations & limitations

* **Evasion:** Attackers could randomize inter-packet times to evade SAI. Combine SAI with other detectors (rate-based, signature-based, anomaly detectors) for defense-in-depth.
* **False positives:** Legitimate automated clients (monitoring services, health-check bots) may show regular intervals — maintain allow-lists and contextual heuristics.
* **IP spoofing / distributed sources:** SAI is particularly effective when abused ips show temporal regularity. For large botnets distributing traffic across many IPs, SAI should be used alongside volumetric detectors.
* **Privacy & logging:** Ensure logging complies with privacy policies / regulations.

---

## Troubleshooting & tuning tips

* If false positives are high: increase tolerance for ∆t equivalence, widen sliding window, or incorporate additional features (packet size variance).
* If false negatives increase: lower detection threshold or increase window size to capture longer patterns.
* For high throughput environments: use approximate counting, sketch-based methods, or sample traffic to reduce memory footprint.

---

## Example: Core idea pseudo-code

```python
# incoming stream of packets: each packet = (src_ip, timestamp)
from collections import deque, defaultdict
window_size = 10
epsilon = 0.01  # seconds: tolerance for equal ∆t
buffers = defaultdict(lambda: deque(maxlen=window_size))

def process_packet(packet):
    ip, ts = packet.src_ip, packet.timestamp
    buf = buffers[ip]
    if buf:
        delta = ts - buf[-1]
        buf.append(ts)
        # compute deltas from buffer and check repetitions
        deltas = [buf[i+1] - buf[i] for i in range(len(buf)-1)]
        repeated_count = count_repetitions(deltas, epsilon)
        score = compute_score(repeated_count, deltas)  # e.g., repeated_count / len(deltas)
        if score > detection_threshold:
            flag_as_attack(ip)
    else:
        buf.append(ts)
```

---

## Further improvements & research directions

* Combine SAI score with network-level features (TCP flags, payload entropy).
* Use lightweight streaming ML (e.g., online learners) for continuous adaptation.
* Integrate with CDN/WAF for automatic mitigation.
* Add adversarial testing to evaluate robustness against timing jitter.

---

## Contact & contributions

* Notebook: [https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing](https://colab.research.google.com/drive/1W6Cgkg5j_ZdeQ7UbE_NLP81VeiIA6B3v?usp=sharing)
* If you want, I can:

  * convert this README into a GitHub-ready `README.md` file, or
  * generate `requirements.txt` and a `sai_detector.py` starter module, or
  * produce a short technical one-pager for non-technical stakeholders.

---

## License

You can add an appropriate license (e.g., MIT) depending on how you want the work shared.

---

