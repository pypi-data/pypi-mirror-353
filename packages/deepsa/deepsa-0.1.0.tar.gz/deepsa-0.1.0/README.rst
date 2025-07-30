DeepSA: A Deep-learning Driven Predictor of Compound Synthesis Accessibility
=======================================================================

DeepSA is a deep learning-based tool for predicting the synthetic accessibility of compounds, helping users evaluate the synthesis difficulty of molecules to select more easily synthesizable molecules for drug discovery and development.

Installation
----

Install DeepSA using pip:

.. code-block:: bash

    pip install deepsa

Usage
-------

1. Predict synthetic accessibility of a single SMILES

.. code-block:: python

    from deepsa import predict_sa
    
    # Predict a single SMILES
    result = predict_sa("CCO")  # Ethanol
    print(f"Synthetic accessibility score: {result['SA_score']:.4f}")
    print(f"Heavy atom count: {result['HA_num']}")
    print(f"Ring count: {result['Ring_num']}")
    print(f"Ring system count: {result['RingSystem_num']}")
    print(f"Rule of five compliance: {result['rule_of_five']}")

2. Predict synthetic accessibility of multiple SMILES

.. code-block:: python

    import pandas as pd
    from deepsa import predict_sa_from_file
    
    # Create DataFrame containing SMILES
    smiles_list = ["CCO", "c1ccccc1", "CC(=O)OC1=CC=CC=C1C(=O)O"]
    df = pd.DataFrame({"smiles": smiles_list})
    
    # Predict and save results
    results = predict_sa_from_file(df, output_path="results.csv")
    print(results[["smiles", "easy", "hard"]])

3. Predict from CSV file

.. code-block:: python

    from deepsa import predict_sa_from_file
    
    # Predict from CSV file (file must contain smiles column)
    results = predict_sa_from_file("compounds.csv")

4. Command line usage

.. code-block:: bash

    # Predict a single SMILES
    deepsa-predict "CCO"
    
    # Predict SMILES from a CSV file
    deepsa-predict compounds.csv --output results.csv

Citation
----

If you use DeepSA in your research, please cite our paper:

Wang, S., Wang, L., Li, F. et al. DeepSA: a deep-learning driven predictor of compound synthesis accessibility. J Cheminform 15, 103 (2023). https://doi.org/10.1186/s13321-023-00771-3

Online Service
-------

We have deployed a pre-trained model at https://bailab.siais.shanghaitech.edu.cn/deepsa for biomedical researchers to conveniently use DeepSA in their research activities.

Users can upload SMILES or CSV files to the server and quickly obtain prediction results.