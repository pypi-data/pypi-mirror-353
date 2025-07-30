
from setuptools import setup, find_packages

setup(
    name="lstm_anomaly_tool",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "tensorflow",
        "joblib"
    ],
    include_package_data=True,
    package_data={"lstm_anomaly_tool": ["*.pkl", "*.h5"]},
    author="djpadovani",
    description="Detecção de anomalias em séries temporais com Autoencoder LSTM",
    long_description="Pacote para aplicar LSTM Autoencoder em séries temporais univariadas.",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
