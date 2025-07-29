
# ChangeLog


## [0.2.0] - Major Update

+ Update setup.py for more robust and maintainable package management.
+ Update requirements to remove `mealpy` dependency.
+ Update GitHub Actions workflows for testing and publishing.
+ Update citation
+ Update `data_preparer` module to include `TimeSeriesDifferencer`, `FeatureEngineering`, and `DataTransformer` classes.
+ Update `scaler` module to include `OneHotEncoder` and `LabelEncoder` classes.

-----------------------------------------------------------------------------------------

## [0.1.0] - Initial Release

The first official release of **PyLWL** includes the following features:

### 📁 Project Structure
- Added essential project files: `CODE_OF_CONDUCT.md`, `MANIFEST.in`, `LICENSE`, `CITATION.cff`, and `requirements.txt`
- Added structured layout for examples, tests, and documentation site

### 🧠 Core Modules
- Implemented shared utility modules:
  - `verifier`: for validating inputs and parameters
  - `scaler`: for feature normalization
  - `scorer`: for evaluation metrics
  - `data_preparer`: for dataset scaling and splitting
  - `kernel`: for defining and managing kernel functions

### 🧱 Base Framework
- Introduced `BaseModel` class in `base_model.py` for consistent model design and shared logic

### 🔍 Core Models
- Implemented classic locally weighted models in `classic_lw.py`:
  - `LwClassifier`: Locally Weighted Classifier
  - `LwRegressor`: Locally Weighted Regressor
- Implemented gradient descent-enhanced variants in `gd_lw.py`:
  - `GdLwClassifier`: Gradient-Descent Locally Weighted Classifier
  - `GdLwRegressor`: Gradient-Descent Locally Weighted Regressor

### 🚀 Tooling & Deployment
- Added GitHub Actions workflow for PyPI publishing
- Added working examples, test cases, and documentation starter site
