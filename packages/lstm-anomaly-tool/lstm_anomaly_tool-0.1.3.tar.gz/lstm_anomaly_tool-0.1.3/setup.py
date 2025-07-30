
from setuptools import setup, find_packages

setup(
    name="lstm_anomaly_tool",
    version="0.1.3",  # MUDE A VERSÃO A CADA PUBLICAÇÃO
    packages=find_packages(),
    install_requires=["numpy", "pandas", "tensorflow", "joblib", "scikit-learn"],
    include_package_data=True,
    package_data={
        "lstm_anomaly_tool": ["*.pkl", "*.json", "*.keras"]
    }
)
