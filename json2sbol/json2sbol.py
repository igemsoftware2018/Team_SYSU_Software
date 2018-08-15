# data: {
#   components: [{
#     'role': xxx,
#     'id': xxx,
#     'name': xxx,
#     'version': xxx,
#     'description': xxx,
#     'sequence': xxx
#   }],
#   lines: [{
#     'name': xxx
#     'structure': [xxx, xxx, xxx]
#   }],
#   promotions: [{
#     'stimulator': xxx, # id of the promotor
#     'other': xxx # id of the material promoted
#   }],
#   inhibitions: [{
#     'inhibitor': xxx, # id of the promotor
#     'other': xxx # id of the material promoted
#   }],
#   combinations: [{
#     'reactants': [xxx, xxx, xxx] # id of the combination reactant
#     'product': xxx # id of the product
#   }],
#   circuit: {
#     'id': xxx, # circuit id if it's already existing, -1 else
#     'name': xxx,
#     'description': xxx
#   }
# }

# import request
# from django.http import HttpRequest
import os
import json
from sbol import *

setHomespace('http://sys-bio.org')
doc = Document()

roles = {
  'DNA': SO_GENE,
  'RNA': SO_SGRNA,
  'promoter': SO_PROMOTER,
  'RBS': SO_RBS,
  'CDS': SO_CDS,
  'terminator': SO_TERMINATOR
}

# data = json.loads(request.POST['data'])

test = open("data.json", encoding='utf-8')
data = json.load(test)

activity = Activity(data['circuit']['name'])
activity.displayId = data['circuit']['name']
activity.description = data['circuit']['description']
doc.addActivity(activity)

# load components
components = {}
for component in data['components']:
  temp = ComponentDefinition(component['id'])
  temp.roles = roles[component['role']]
  temp.description = component['description']
  temp.sequence = Sequence(component['id'], component['sequence'])
  components[component['id']] = temp
  doc.addComponentDefinition(temp)

# load line structure
for line in data['lines']:
  structure = []
  circuit = ComponentDefinition(line['name'])
  doc.addComponentDefinition(circuit)
  for temp in line['structure']:
    structure.append(components[temp])
  circuit.assemblePrimaryStructure(structure)

# functional components
pro_fcs = {}
inh_fcs = {}
com_fcs = {}

# promotion
if 'promotions' in data.keys():
  proModule = ModuleDefinition('promotion_module')
  doc.addModuleDefinition(proModule)

  for index, promotion in enumerate(data['promotions']):
    stimulatorName = promotion['stimulator']
    otherName = promotion['other']
    
    if not stimulatorName in pro_fcs.keys():
      stimulator_fc = proModule.functionalComponents.create(stimulatorName)
      stimulator_fc.definition = components[stimulatorName].identity
      stimulator_fc.access = SBOL_ACCESS_PUBLIC
      stimulator_fc.direction = SBOL_DIRECTION_IN_OUT
      pro_fcs[stimulatorName] = stimulator_fc

    if not otherName in pro_fcs.keys():
      other_fc = proModule.functionalComponents.create(otherName)
      other_fc.definition = components[otherName].identity
      other_fc.access = SBOL_ACCESS_PUBLIC
      other_fc.direction = SBOL_DIRECTION_IN_OUT
      pro_fcs[otherName] = other_fc

    proInteraction = proModule.interactions.create('promotion_' + str(index))
    proInteraction.types = SBO_STIMULATION

    stimulator_participation = proInteraction.participations.create(stimulatorName)
    stimulator_participation.roles = SBO_STIMULATOR
    stimulator_participation.participant = pro_fcs[stimulatorName].identity

    other_participation = proInteraction.participations.create(otherName)
    other_participation.roles = components[otherName].roles
    other_participation.participant = pro_fcs[otherName].identity

# inhibition
if 'inhibitions' in data.keys():
  inhModule = ModuleDefinition('inhbition_module')
  doc.addModuleDefinition(inhModule)

  for index, inhibition in enumerate(data['inhibitions']):
    inhibitorName = inhibition['inhibitor']
    otherName = inhibition['other']
    
    if not inhibitorName in inh_fcs.keys():
      inhibitor_fc = inhModule.functionalComponents.create(inhibitorName)
      inhibitor_fc.definition = components[inhibitorName].identity
      inhibitor_fc.access = SBOL_ACCESS_PUBLIC
      inhibitor_fc.direction = SBOL_DIRECTION_IN_OUT
      inh_fcs[inhibitorName] = inhibitor_fc

    if not otherName in inh_fcs.keys():
      other_fc = inhModule.functionalComponents.create(otherName)
      other_fc.definition = components[otherName].identity
      other_fc.access = SBOL_ACCESS_PUBLIC
      other_fc.direction = SBOL_DIRECTION_IN_OUT
      inh_fcs[otherName] = other_fc

    inhInteraction = inhModule.interactions.create('inhibition_' + str(index))
    inhInteraction.types = SBO_INHIBITION

    inhibitor_participation = inhInteraction.participations.create(inhibitorName)
    inhibitor_participation.roles = SBO_INHIBITOR
    inhibitor_participation.participant = inh_fcs[inhibitorName].identity

    other_participation = inhInteraction.participations.create(otherName)
    other_participation.roles = components[otherName].roles
    other_participation.participant = inh_fcs[otherName].identity

# combination
if 'combinations' in data.keys():
  comModule = ModuleDefinition('combination_module')
  doc.addModuleDefinition(comModule)

  for index, combination in enumerate(data['combinations']):
    comInteraction = comModule.interactions.create('combination_' + str(index))
    comInteraction.role = SBO_NONCOVALENT_BINDING
    for reactant in combination['reactants']:
      if not reactant in com_fcs.keys():
        reactant_fc = comModule.functionalComponents.create(reactant)
        reactant_fc.definition = components[reactant].identity
        reactant_fc.access = SBOL_ACCESS_PUBLIC
        reactant_fc.direction = SBOL_DIRECTION_IN_OUT
        com_fcs[reactant] = reactant_fc
      reactant_participation = comInteraction.participations.create(reactant)
      reactant_participation.roles = SBO_REACTANT
      reactant_participation.participant = com_fcs[reactant].identity
    
    product = combination['product']
    if not product in com_fcs.keys():
      product_fc = comModule.functionalComponents.create(product)
      product_fc.definition = components[product].identity
      product_fc.access = SBOL_ACCESS_PUBLIC
      product_fc.direction = SBOL_DIRECTION_IN_OUT
      com_fcs[product] = product_fc
    product_participation = comInteraction.participations.create(product)
    product_participation.roles = SBO_PRODUCT
    product_participation.participant = com_fcs[product].identity
    

# create sbol document
circuit_name = data['circuit']['name']
filename = circuit_name + '.xml'
result = doc.write(filename)
print(result)

# response = HttpResponse(open(filename,"rb"),content_type="text/xml")

# if os.path.exists(filename):
#   os.remove(filename)

# return response