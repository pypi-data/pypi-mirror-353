import anndata as ad  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from scipy.sparse import csr_matrix  # type: ignore
import subprocess
import os

# Get current working directory
current_path = os.getcwd()

# Build a new path by appending a folder name
new_path = os.path.join(current_path, "FinalPackage", "rnadtu")

# Change into that directory
os.chdir(new_path)

print(os.getcwd())


def sparseToCsv(sparseMatrix, csvName):

    # Convert sparse matrix to an array
    arrayMatrix = sparseMatrix.toarray()

    # Convert array to a DataFrame
    df = pd.DataFrame(arrayMatrix)

    # Export to csv
    df.to_csv(f'{csvName}.csv', index=False)


def cidr(aData, layer=None):
    print("Algorithm Starting...")
    # Udfør CIDR på aData.X hvis intet lag er specificeret
    data = aData.X if layer is None else aData.layers[layer]
    sparse_matrix = csr_matrix(data, dtype=np.float32)
    sparseToCsv(sparse_matrix, 'annDataToCSV')
    print(subprocess.run(["Rscript", "module2.R"], check=True).stderr)


annD = ad.io.read_csv("symsim_observed_counts_5000genes_1000cells_complex.csv",
                      delimiter=',', first_column_names=None, dtype='float32')
    

cidr(annD)
