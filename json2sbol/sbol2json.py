from sbol import *
import json

filename = 'test_gene'

doc = Document()
doc.read(filename + '.xml')

roles = {
  'http://identifiers.org/so/SO:0000704': 'DNA',
  'http://identifiers.org/so/SO:0000167': 'PRO',
  'http://identifiers.org/so/SO:0001998': 'RNA',
  'http://identifiers.org/so/SO:0000141': 'TER',
  'http://identifiers.org/so/SO:0000316': 'CDS',
  'http://identifiers.org/so/SO:0000139': 'RBS'
}

interaction_roles = {
  'http://identifiers.org/biomodels.sbo/SBO:0000020': 'inhibitor',
  'http://identifiers.org/biomodels.sbo/SBO:0000459': 'stimulator',
  'http://identifiers.org/biomodels.sbo/SBO:0000010': 'reactants'
}

interaction_types = {
  'http://identifiers.org/biomodels.sbo/SBO:0000343': 'combination',
  'http://identifiers.org/biomodels.sbo/SBO:0000169': 'inhbition',
  'http://identifiers.org/biomodels.sbo/SBO:0000170': 'promotion'

}

data = {
  "components": [],
  "lines": [],
  "circuit": {
    "id": 1,
    "name": "",
    "description": ""
  },
  "promotions": [],
  "inhibitions": [],
  "combinations": []
}

# tranform componentDefinitions
for x in doc:
  # print(str(x))
  if 'Activity' in str(x):
    temp = doc.getActivity(str(x))
    data['circuit']['name'] = temp.displayId
    data['circuit']['id'] = temp.displayId
    data['circuit']['description'] = temp.description
  elif 'ComponentDefinition' in str(x):
    temp = doc.getComponentDefinition(str(x))
    component = {}
    line = {
      "structure": []
    }
    if temp.roles: # components
      roleUri = temp.roles[0]
      if (roleUri in roles.keys()):
        component['role'] = roles[roleUri]
      component['id'] = temp.displayId
      component['name'] = temp.displayId
      component['version'] = temp.version
      component['description'] = temp.description
      sequenceUri = temp.sequences
      if sequenceUri:
        component['sequence'] = doc.getSequence(sequenceUri[0]).elements
      data['components'].append(component)
    else: # lines
      line['name'] = temp.displayId
      line_comp = {}
      for comp in temp.components:
        line_comp[str(comp)] = doc.getComponentDefinition(comp.definition).displayId
      for index, constraint in enumerate(temp.sequenceConstraints):
        if (index == 0):
          line['structure'].append(line_comp[constraint.subject])
          line['structure'].append(line_comp[constraint.object])
        else:
          line['structure'].append(line_comp[constraint.object])
      data['lines'].append(line)
  elif 'ModuleDefinition' in str(x):
    temp = doc.getModuleDefinition(str(x))
    for action in temp.interactions:
      if interaction_types[action.types[0]] == 'inhbition':
        inh = {}
        for part in action.participations:
          if part.roles[0] in interaction_roles.keys():
            inh[interaction_roles[part.roles[0]]] = part.displayId
          else:
            inh['other'] = part.displayId
        data['inhibitions'].append(inh)
      elif interaction_types[action.types[0]] == 'promotion':
        pro = {}
        for part in action.participations:
          if part.roles[0] in interaction_roles.keys():
            pro[interaction_roles[part.roles[0]]] = part.displayId
          else:
            pro['other'] = part.displayId
        data['promotions'].append(pro)
      elif interaction_types[action.types[0]] == 'combination':
        com = {
          'reactants': []
        }
        for part in action.participations:
          if part.roles[0] in interaction_roles.keys():
            com[interaction_roles[part.roles[0]]].append(part.displayId)
          else:
            com['other'] = part.displayId
        data['combinations'].append(com)

data['circuit']['name'] = filename

json = json.dumps(data)
print(json)