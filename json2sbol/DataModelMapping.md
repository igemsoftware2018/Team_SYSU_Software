# Data Model Mapping json

```python
class Parts(models.Model): # map to components
  Role = models.CharField(max_length = 20) # new add
  Name = models.CharField(max_length = 50, unique = True, db_index = True) # Name also the id
  Type = models.CharField(max_length = 20)
  Description = models.TextField()
  Sequence = models.TextField()
  secondName = models.TextField(default="Unknow")
  Length = models.IntegerField(default = 0) # 0输出Unknow
  Part_rating = models.IntegerField(default = 0)#0输出Unknow
  Safety = models.IntegerField(default = -1) #负数的时候需要输出Unknow
  Scores = models.FloatField(default=-1.0) # 负数的时候需要输出Unknow
  Release_status = models.CharField(max_length = 100, default = "To be add")
  Twins = models.CharField(max_length = 500, default = "To be add")
  Sample_status = models.CharField(max_length = 50, default = "To be add")
  Part_results = models.CharField(max_length = 16, default = "To be add")
  Use = models.CharField(max_length = 50, default = "To be add")
  Group = models.CharField(max_length = 100, default = "To be add")
  Author = models.CharField(max_length = 256, default = "To be add")
  DATE = models.CharField(max_length = 10, default = "To be add")
  Distribution = models.TextField(default = "To be add")
  Parameter = models.TextField(default = "")

class PartsInteract(models.Model): # known interactions
  parent = models.ForeignKey('Parts', related_name = 'parent_part', on_delete = models.CASCADE)
  child = models.ForeignKey('Parts', related_name = 'child_part', on_delete = models.CASCADE)
  InteractType = models.CharField(max_length=10, default="normal")
  Score = models.FloatField(default=-1.0) #负数的时候需要输出Unknow

class Circuit(models.Model): # map to circuit
  Name = models.CharField(max_length = 50, unique = False)
  Description = models.CharField(max_length = 100)
  Author = models.ForeignKey('User', on_delete = models.CASCADE, null = True)

class CircuitDevices(models.Model): # map to lines
  Circuit = models.ForeignKey('Circuit', on_delete = models.CASCADE)
  # Subparts store the circuitParts and circuitParts maps to Part
  # Remember to retrieve the Id of the Part when try to transform sbol
  Subparts = models.ManyToManyField(CircuitParts) # map to structure
  X = models.IntegerField(default = 0)
  Y = models.IntegerField(default = 0)

class CircuitLines(models.Model): # map to stimulations & inhibitions
  Start = models.ForeignKey('CircuitParts', related_name = 'Start', on_delete = models.CASCADE) # map to stimulator or inhibitor
  End = models.ForeignKey('CircuitParts', related_name = 'End', on_delete = models.CASCADE) # map to other
  Type = models.CharField(max_length = 20) # stimulation or inhibition

class CircuitCombines(models.Model): # map to combinations
  Circuit = models.ForeignKey('Circuit', on_delete = models.CASCADE, related_name = "Father")
  Father = models.ForeignKey('CircuitParts', on_delete = models.CASCADE, related_name = "Sons") # Father is the product
  Sons = models.ManyToManyField(CircuitParts) # Sons are reactants
```

```json
{
  "components": [{
    "role": xxx,
    "id": xxx,
    "name": xxx,
    "version": xxx,
    "description": xxx,
    "sequence": xxx
  }],
  "lines": [{
    "name": xxx,
    "structure": [xxx, xxx, xxx]
  }],
  "stimulations": [{
    "stimulator": xxx,
    "other": xxx
  }],
  "inhibitions": [{
    "inhibitor": xxx,
    "other": xxx
  }],
  "combinations": [{
    "reactants": [xxx, xxx, xxx],
    "production": xxx
  }],
  "circuit": {
    "id": xxx,
    "name": xxx,
    "description": xxx
  }
}
```