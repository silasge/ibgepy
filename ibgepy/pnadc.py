import os
from typing import Dict, List
from numpy import nan
import pandas as pd


class PnadcCodebook:
    """A class used to perform operations on the Pnad Continua's codebook files
    which is needed to read its microdata files

    Attributes:
        codebook: a Pandas' DataFrame with raw informations from the codebook
        widths: a list of integers with the positions of each column in the
            Pnad Continua's microdata or a None value if the method .get_widths
            was not called yet
        names: a list of strings with the name of each column in the Pnad Continua's
            microdata or a None value if the method .get_names was not called yet
        labels: a dict of dicts with the names of each column and the patterns to
            replace values with its original labels
    """

    def __init__(self, codebook_filepath: str) -> None:
        """Inits PnadcCodebook with a path to the codebook

        Args:
            codebook_filepath (str): A string giving the path to the codebook file
        """
        self.codebook = pd.read_excel(
            codebook_filepath, skiprows=3, usecols=[0, 1, 2, 4, 5, 6]
        ).rename(
            columns={
                "Parte 1 - Identificação e Controle": "pos_inicial",
                "Unnamed: 1": "tamanho",
                "Unnamed: 2": "cod_var",
                "Unnamed: 4": "descricao",
                "Unnamed: 5": "categoria",
                "Unnamed: 6": "descr_categoria",
            }
        )
        self.widths = None
        self.names = None
        self.labels = None

    def get_widths(self) -> List[int]:
        """Get the positions of each column in the Pnad Continua's microdata

        Returns:
            List[int]: a list of integers with each position
        """
        self.widths = self.codebook["tamanho"].dropna().astype("int").to_list()
        return self.widths

    def get_names(self) -> List[str]:
        """Get the names of each column in the Pnad Continua's microdata

        Returns:
            List[str]: a list of strings with each name
        """
        self.names = self.codebook["cod_var"].dropna().to_list()
        return self.names

    def get_labels(self) -> Dict[str, Dict[float, str]]:
        """Get the names of each column and the patterns to replace values
        with its original labels

        Returns:
            Dict[str, Dict[float, str]]: A dict of dicts giving the patterns
        """
        dict_labels = (
            self.codebook[["cod_var", "categoria", "descr_categoria"]]
            .apply(
                lambda x: pd.to_numeric(x, errors="coerce")
                if x.name == "categoria"
                else x
            )
            .dropna(subset="categoria")
            .replace(to_replace={"descr_categoria": {"Não informado": nan}})
        )
        dict_labels["cod_var"] = dict_labels["cod_var"].fillna(method="ffill")
        self.labels = (
            dict_labels.groupby("cod_var")
            .apply(
                lambda x: {
                    tr: v for (tr, v) in zip(x["categoria"], x["descr_categoria"])
                }
            )
            .to_dict()
        )
        return self.labels


def read_pnadc(
    microdata_filepath: str, codebook_filepath: str, label_values: bool = True, **kwargs
) -> pd.DataFrame:
    """A function to read the pnad continua's microdata.

    Args:
        microdata_filepath (str): A string with the path to the microdata file.
        codebook_filepath (str): A string with the path to the codebook file.
        label_values (bool, optional): If True, returns all the labels from the
            microdata, otherwise if False. Defaults to True.
        kwargs: Any optional keyword argument that can be passed to Pandas's TextFileReader

    Raises:
        FileNotFoundError: If the patch doesn't exist.
        TypeError: if the type of the argument provided is from the wrong type.

    Returns:
        pd.DataFrame: A Pandas DataFrame with the Pnad Continua's Survey
    """
    # Check microdata_path
    if isinstance(microdata_filepath, str):
        if not os.path.exists(microdata_filepath):
            raise FileNotFoundError("The path to the microdata file doesn't exist.")
    else:
        raise TypeError(
            f"microdata_filepath must be a str and not {type(microdata_filepath)}."
        )

    # Check codebook_filepath
    if isinstance(codebook_filepath, str):
        if not os.path.exists(codebook_filepath):
            raise FileNotFoundError("The path to the codebook file doesn't exist.")
    else:
        raise TypeError(
            f"microdata_path must be a str and not {type(codebook_filepath)}."
        )

    # Check label_values
    if not isinstance(label_values, bool):
        raise TypeError("label_values bust be a boolean (True or False)")

    pnadc_dict = PnadcCodebook(codebook_filepath=codebook_filepath)
    widths = pnadc_dict.get_widths()
    col_names = pnadc_dict.get_names()

    pnadc = pd.read_fwf(
        filepath_or_buffer=microdata_filepath, widths=widths, names=col_names, **kwargs
    )

    if label_values:
        labels = pnadc_dict.get_labels()
        pnadc = pnadc.replace(to_replace=labels)

    return pnadc