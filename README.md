# ibgepy

ibgepy is a python package to facilitate the reading of microdata from the Brazilian Institute of Geography and Statistics (IBGE).

# Installation


# Examples


## Pnad Continua

The files must be downloaded from [ibge](https://www.ibge.gov.br/estatisticas/sociais/trabalho/9171-pesquisa-nacional-por-amostra-de-domicilios-continua-mensal.html) webpage.

You'll need two files. The microdata itself in `.txt` and the codebook (dicionário in portuguese) in `.xls`.


``` python
from ibgepy import read_pnadc

pnadc = read_pnadc(
    microdata_filepath="path/to/pnadc_microdata.txt",
    codebook_filepath="path/to/pnadc_codebook.xls",
    label_values = True
)
```

Also, you can specify any keyword argument that can be passed to Pandas `TextFileReader` as well.

For example, you can select the columns you need and the number of lines to read.

``` python
pnadc = read_pnadc(
    microdata_filepath="path/to/pnadc_microdata.txt",
    codebook_filepath="path/to/pnadc_codebook.xlsx",
    label_values = True,
    usecols = ["UF", "VD4017"],
    nrows = 10000
)
```

# To-do

- [x] Pnad Contínua
- [] POF
- [] PNS