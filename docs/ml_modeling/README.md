
## Epic: ML Labeling & Modeling

12. 🔴 **As a Data Scientist**, I want to generate historical buy/hold/sell labels based on rule-counts so that I have ground truth for the past 20 years.

    * **Acceptance**: Column `label` with values in {buy, hold, sell} populates for each quarterly row.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
  
13. 🔴 **As a Data Scientist**, I want to build and evaluate a LightGBM classifier on this labeled data so that I can predict labels on new quarters.

    * **Acceptance**: Model training script runs, outputs accuracy/precision/recall via cross-validation.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
  
14. 🔴 **As a Data Scientist**, I want to serialize the trained model to disk so that the serving layer can load it.

    * **Acceptance**: `model.pkl` (or equivalent) saved to artifact storage.
   *  **Docs**: 
   * **Status**: 🔴 
   * **Priority**: 🔴
  
  Absolutely, Todd. Here's a complete set of **user stories** aligned with your plan: train a dividend-predicting ML model on your dev machine and deploy the inference pipeline to a Raspberry Pi. These stories cover **modeling, feature engineering, training, deployment, and usage**—all mapped to real tasks.

---

## 📘 **Epic: Predict Future Dividend Performance for Buy-Signal Stocks**

---

### **1. As a quant developer, I want to train a model on my dev machine...**

#### 🔹 *...so I can predict combined dividend yield and growth two years into the future.*

* **Story 1.1**:
  *As a quant developer, I want to use 20 years of quarterly stock fundamentals, dividends, and financial ratios as features, so the model learns from long-term trends.*

* **Story 1.2**:
  *As a quant developer, I want to create lagged, rolling, and delta features for each stock/quarter, so the model captures momentum and growth signals.*

* **Story 1.3**:
  *As a quant developer, I want to train an XGBoost or LightGBM regression model, so I can accurately forecast dividend performance.*

* **Story 1.4**:
  *As a quant developer, I want to evaluate my model using RMSE and R² on a time-split validation set, so I ensure realistic forward-looking accuracy.*

* **Story 1.5**:
  *As a quant developer, I want to analyze feature importance and SHAP values, so I can validate that the model aligns with financial intuition.*

---

### **2. As an engineer, I want to export the trained model...**

#### 🔹 *...so I can deploy it to the Raspberry Pi for fast, lightweight inference.*

* **Story 2.1**:
  *As an engineer, I want to save the trained model to a portable format (`.txt` for LightGBM or `.pkl` for XGBoost), so I can deploy it on ARM-based devices.*

* **Story 2.2**:
  *As an engineer, I want to serialize my feature engineering pipeline, so the same logic runs consistently during inference.*

---

### **3. As a platform engineer, I want to install the inference environment on the Raspberry Pi...**

#### 🔹 *...so I can make predictions locally with minimal resources.*

* **Story 3.1**:
  *As a platform engineer, I want to install only lightweight dependencies (numpy, pandas, lightgbm), so I avoid overloading the Pi.*

* **Story 3.2**:
  *As a platform engineer, I want to test loading the model and scoring a batch of feature vectors, so I can validate the setup without full retraining.*

---

### **4. As a user or analyst, I want to score stocks flagged by the rules engine...**

#### 🔹 *...so I can rank buy candidates by projected dividend performance.*

* **Story 4.1**:
  *As a user, I want to feed the model a list of stocks marked as "buy" by my existing rules engine, so I only evaluate relevant candidates.*

* **Story 4.2**:
  *As a user, I want to get back a ranked list of stocks with predicted 2Y dividend yield + growth, so I can select the top income-generating opportunities.*

* **Story 4.3**:
  *As a user, I want to set a threshold for the predicted value, so I can filter out underperformers.*

---

### **5. (Optional) As a tech-savvy user, I want to expose this as a CLI or API...**

#### 🔹 *...so I can run predictions on demand or hook into other systems.*

* **Story 5.1**:
  *As a user, I want to run a command-line tool on the Pi that scores a CSV of stock data and outputs predictions to a file.*

* **Story 5.2**:
  *As a developer, I want to build a simple Flask API on the Pi, so I can send a ticker and get back the predicted dividend score.*

---

## 📌 Notes

* These stories are modular—if you’re agile, you can work through them in sprints (Modeling → Export → Inference → Interface).
* You can also tag these by role: quant, ML engineer, platform/devops, user.

---

Would you like me to wrap this as a Markdown user story board you can drop into Jira or GitHub Projects? Or need acceptance criteria for each one?
