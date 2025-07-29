# PyCodeML

**PyCodeML** is a Python package designed to automate the training, evaluation, tuning, and selection of the best-performing machine learning models for regression and classification tasks. It simplifies the process of model training, comparison, tuning, and deployment.

## ✅ Features

- Supports **Regression** and *(soon)* **Classification** tasks  
- Evaluates multiple models and selects the best one  
- **Hyperparameter tuning** support for optimized performance  
- Saves and loads trained models for future use  
- Simple and intuitive API for fast prototyping and deployment  

## 📦 Installation

```bash
pip install pycodeml
```
💻 Usage

1️⃣ Train and Save the Best Model
```bash
import pandas as pd
from pycodeml.regressor import RegressorTrainer  # For regression tasks

# Load dataset from a CSV file (Ensure target column exists)
df = pd.read_csv("data.csv")

# Initialize and train the model
trainer = RegressorTrainer(df, "target", data_sample_percent=100)
best_model = trainer.train_and_get_best_model()

# Save the best model
trainer.save_best_model("best_model.pkl")
```
2️⃣ Load and Use the Saved Model
```bash
import pandas as pd
from pycodeml.utils import load_model

# Load the saved model
model = load_model("best_model.pkl")

# Load new data from a CSV file (without target column)
new_data = pd.read_csv("new_data.csv")

# Make predictions
prediction = model.predict(new_data)
print("Predicted Values:", prediction)
```
3️⃣ Tune the Best Model
```bash
from pycodeml.tunner import RegressorTuner

# Perform hyperparameter tuning on the best model
tuner = RegressorTuner(
    model=best_model,
    dataset=df,
    target_column="target",
    model_name="Random Forest"  # Must match one of the supported models
)

# Get the tuned model
tuned_model,score = tuner.tune()
```
📊 Supported Models
Regression
- Linear Regression  
- Decision Tree Regressor  
- Random Forest Regressor  
- Support Vector Machine (SVR)  
- Gradient Boosting Regressor  
- Ridge Regression  
- Lasso Regression  
- Elastic Net 

Classification (Coming Soon)
Logistic Regression

- Logistic Regression  
- Random Forest Classifier  
- Support Vector Machine (SVM)  
- Gradient Boosting Classifier  
- K-Nearest Neighbors (KNN)  

🤝 Contributing
Contributions are welcome!
If you'd like to improve this package, feel free to fork the repository and submit a pull request.

🔗 GitHub: https://github.com/Nachiket858/PyCodeML

