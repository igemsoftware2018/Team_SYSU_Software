# Json data to SBOL data

The file *json2sbol.py* can transform a json data to sbol data following the json data restriction.

The restriction of the json data is commentted in the head of the *json2sbol.py* file

## Requirement

1. platform

    windows(mine) / linux / macOS

1. python

    (python 3.6.6 for me)

1. pysbol

    ```pip install pysbol``` can install the pysbol  
    *pysbol only support python 2.7 and python 3.6*

## Testcase

```json
{
    "components": [
        {
            "role": "PRO",
            "id": "I14034",
            "name": "I14034",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        },
        {
            "role": "PRO",
            "id": "I14033",
            "name": "I14033",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        },
        {
            "role": "PRO",
            "id": "I14032",
            "name": "I14032",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        },
        {
            "role": "CDS",
            "id": "I14031",
            "name": "I14031",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        },
        {
            "role": "TER",
            "id": "I14030",
            "name": "I14030",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        },
        {
            "role": "TER",
            "id": "I14029",
            "name": "I14029",
            "version": 1,
            "description": "test",
            "sequence": "atcg"
        }
    ],
    "lines": [
        [
            "I14032",
            "I14031",
            "I14030"
        ]
    ],
    "circuit": {
        "id": 1,
        "name": "test_gene",
        "description": "test circuit"
    },
    "promotions": [
        {
            "stimulator": "I14032",
            "other": "I14031"
        },
        {
            "stimulator": "I14030",
            "other": "I14031"
        }
    ],
    "inhibitions": [
        {
            "inhibitor": "I14031",
            "other": "I14029"
        },
        {
            "inhibitor": "I14034",
            "other": "I14030"
        }
    ],
    "combinations": [
        {
            "reactants": [
                "I14034",
                "I14029",
                "I14033"
            ]
        }
    ]
}
```

## Result

Print in the test_gene xml document