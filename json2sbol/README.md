# Json data to SBOL data

The file *json2sbol.py* can transform a json data to sbol data following the json data restriction.

## Requirement

1. platform

    windows(mine) / linux / macOS

1. python

    (python 3.6.6 for me)

1. pysbol

    ```pip install pysbol``` can install the pysbol  
    *pysbol only support python 2.7 and python 3.6*

## Json Restriction

```JSON
{
  "components": [{
    "role": "xxx",
    "id": "xxx",
    "name": "xxx",
    "version": "xxx",
    "description": "xxx",
    "sequence": "xxx"
  }],
  "lines": [{
    "name": "xxx"
    "structure": ["xxx", "xxx", "xxx"]
  }],
  "promotions": [{
    "stimulator": "xxx", # id of the promotor
    "other": "xxx" # id of the material promoted
  }],
  "inhibitions": [{
    "inhibitor": "xxx", # id of the promotor
    "other": "xxx" # id of the material promoted
  }],
  "combinations": [{
    "reactants": ["xxx", "xxx", "xxx"] # id of the combination reactant
    "production": "xxx" # id of the production
  }],
  "circuit": {
    "id": "xxx", # circuit id if it's already existing, -1 else
    "name": "xxx",
    "description": "xxx"
  }
}
```

## Testcase

Included in data.json file

## Result

Print in the test_gene xml document