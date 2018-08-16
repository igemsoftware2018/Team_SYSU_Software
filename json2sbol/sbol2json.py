from sbol import *
import json

filename = 'test_gene'

doc = Document()
doc.read(filename + '.xml')

so_dict = {
  'http://identifiers.org/so/SO:0000167': 'Promoter',
  'http://identifiers.org/so/SO:0000057': 'operator',
  'http://identifiers.org/so/SO:0000316': 'CDS',
  'http://identifiers.org/so/SO:0000204': 'fivePrimeUtr',
  'http://identifiers.org/so/SO:0000141': 'Terminator',
  'http://identifiers.org/so/SO:0000627': 'insulator',
  'http://identifiers.org/so/SO:0000296': 'originOfReplication',
  'http://identifiers.org/so/SO:0005850': 'primerBindingSite',
  'http://identifiers.org/so/SO:0000139': 'RBS',
  'http://identifiers.org/so/SO:0000704': 'gene',
  'http://identifiers.org/so/SO:0000234': 'mRNA',
  'http://identifiers.org/so/SO:0001687': 'restrictionEnzymeRecognitionSite',
  'http://identifiers.org/so/SO:0000280': 'engineeredGene',
  'http://identifiers.org/so/SO:0000804': 'engineeredRegion',
  'http://identifiers.org/so/SO:0000110': 'sequenceFeature',
  'http://identifiers.org/so/SO:0001998': 'SGRNA'
}

sbo_dict = {
  'http://identifiers.org/biomodels.sbo/SBO:0000004': 'modelingFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000062': 'continuousFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000293': 'nonSpatialContinuousFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000292': 'spatialContinuousFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000063': 'discreteFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000295': 'nonSpatialDiscreteFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000294': 'spatialDiscreteFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000624': 'fluxBalanceFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000234': 'logicalFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000547': 'booleanLogicalFramework',
  'http://identifiers.org/biomodels.sbo/SBO:0000231': 'occurringEntityRepresentation',
  'http://identifiers.org/biomodels.sbo/SBO:0000412': 'biologicalActivity',
  'http://identifiers.org/biomodels.sbo/SBO:0000375': 'process',
  'http://identifiers.org/biomodels.sbo/SBO:0000167': 'biochemicalOrTransportReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000176': 'biochemicalReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000208': 'acidBaseReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000213': 'deprotonation',
  'http://identifiers.org/biomodels.sbo/SBO:0000212': 'protonation',
  'http://identifiers.org/biomodels.sbo/SBO:0000181': 'conformationalTransition',
  'http://identifiers.org/biomodels.sbo/SBO:0000182': 'conversion',
  'http://identifiers.org/biomodels.sbo/SBO:0000210': 'additionOfAChemicalGroup',
  'http://identifiers.org/biomodels.sbo/SBO:0000215': 'acetylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000217': 'glycosylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000233': 'hydroxylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000214': 'methylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000219': 'myristoylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000218': 'palmitoylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000216': 'phosphorylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000221': 'prenylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000222': 'farnesylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000223': 'geranylgeranylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000220': 'sulfation',
  'http://identifiers.org/biomodels.sbo/SBO:0000224': 'ubiquitination',
  'http://identifiers.org/biomodels.sbo/SBO:0000178': 'cleavage',
  'http://identifiers.org/biomodels.sbo/SBO:0000211': 'removalOfAChemicalGroup',
  'http://identifiers.org/biomodels.sbo/SBO:0000401': 'deamination',
  'http://identifiers.org/biomodels.sbo/SBO:0000400': 'decarbonylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000399': 'decarboxylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000330': 'dephosphorylation',
  'http://identifiers.org/biomodels.sbo/SBO:0000402': 'transferOfAChemicalGroup',
  'http://identifiers.org/biomodels.sbo/SBO:0000403': 'transamination',
  'http://identifiers.org/biomodels.sbo/SBO:0000179': 'degradation',
  'http://identifiers.org/biomodels.sbo/SBO:0000180': 'dissociation',
  'http://identifiers.org/biomodels.sbo/SBO:0000376': 'hydrolysis',
  'http://identifiers.org/biomodels.sbo/SBO:0000209': 'ionisation',
  'http://identifiers.org/biomodels.sbo/SBO:0000377': 'isomerisation',
  'http://identifiers.org/biomodels.sbo/SBO:0000177': 'nonCovalentBinding',
  'http://identifiers.org/biomodels.sbo/SBO:0000200': 'redoxReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000201': 'oxidation',
  'http://identifiers.org/biomodels.sbo/SBO:0000202': 'reduction',
  'http://identifiers.org/biomodels.sbo/SBO:0000185': 'transportReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000588': 'transcellularMembraneEffluxReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000587': 'transcellularMembraneInfluxReaction',
  'http://identifiers.org/biomodels.sbo/SBO:0000357': 'biologicalEffectOfAPerturbation',
  'http://identifiers.org/biomodels.sbo/SBO:0000205': 'compositeBiochemicalProcess',
  'http://identifiers.org/biomodels.sbo/SBO:0000204': 'dnaReplication',
  'http://identifiers.org/biomodels.sbo/SBO:0000589': 'geneticProduction',
  'http://identifiers.org/biomodels.sbo/SBO:0000183': 'transcription',
  'http://identifiers.org/biomodels.sbo/SBO:0000184': 'translation',
  'http://identifiers.org/biomodels.sbo/SBO:0000395': 'encapsulatingProcess',
  'http://identifiers.org/biomodels.sbo/SBO:0000342': 'molecularOrGeneticInteraction',
  'http://identifiers.org/biomodels.sbo/SBO:0000343': 'geneticInteraction',
  'http://identifiers.org/biomodels.sbo/SBO:0000501': 'geneticEnhancement',
  'http://identifiers.org/biomodels.sbo/SBO:0000500': 'geneticSuppression',
  'http://identifiers.org/biomodels.sbo/SBO:0000502': 'syntheticLethality',
  'http://identifiers.org/biomodels.sbo/SBO:0000344': 'molecularInteraction',
  'http://identifiers.org/biomodels.sbo/SBO:0000526': 'proteinComplexFormation',
  'http://identifiers.org/biomodels.sbo/SBO:0000397': 'omittedProcess',
  'http://identifiers.org/biomodels.sbo/SBO:0000358': 'phenotype',
  'http://identifiers.org/biomodels.sbo/SBO:0000464': 'stateVariableAssignment',
  'http://identifiers.org/biomodels.sbo/SBO:0000591': 'petriNetTransition',
  'http://identifiers.org/biomodels.sbo/SBO:0000396': 'uncertainProcess',
  'http://identifiers.org/biomodels.sbo/SBO:0000374': 'relationship',
  'http://identifiers.org/biomodels.sbo/SBO:0000168': 'control',
  'http://identifiers.org/biomodels.sbo/SBO:0000239': 'allostericControl',
  'http://identifiers.org/biomodels.sbo/SBO:0000394': 'consumption',
  'http://identifiers.org/biomodels.sbo/SBO:0000169': 'inhibition',
  'http://identifiers.org/biomodels.sbo/SBO:0000407': 'absoluteInhibition',
  'http://identifiers.org/biomodels.sbo/SBO:0000393': 'production',
  'http://identifiers.org/biomodels.sbo/SBO:0000170': 'stimulation',
  'http://identifiers.org/biomodels.sbo/SBO:0000411': 'absoluteStimulation',
  'http://identifiers.org/biomodels.sbo/SBO:0000172': 'catalysis',
  'http://identifiers.org/biomodels.sbo/SBO:0000171': 'necessaryStimulation',
  'http://identifiers.org/biomodels.sbo/SBO:0000392': 'equivalence',
  'http://identifiers.org/biomodels.sbo/SBO:0000237': 'logicalCombination',
  'http://identifiers.org/biomodels.sbo/SBO:0000173': 'and',
  'http://identifiers.org/biomodels.sbo/SBO:0000238': 'not',
  'http://identifiers.org/biomodels.sbo/SBO:0000174': 'or',
  'http://identifiers.org/biomodels.sbo/SBO:0000175': 'xor',
  'http://identifiers.org/biomodels.sbo/SBO:0000398': 'logicalRelationship',
  'http://identifiers.org/biomodels.sbo/SBO:0000413': 'positionalRelationship',
  'http://identifiers.org/biomodels.sbo/SBO:0000414': 'cis',
  'http://identifiers.org/biomodels.sbo/SBO:0000469': 'containment',
  'http://identifiers.org/biomodels.sbo/SBO:0000415': 'trans',
  'http://identifiers.org/biomodels.sbo/SBO:0000003': 'participantRole',
  'http://identifiers.org/biomodels.sbo/SBO:0000289': 'functionalCompartment',
  'http://identifiers.org/biomodels.sbo/SBO:0000019': 'modifier',
  'http://identifiers.org/biomodels.sbo/SBO:0000595': 'dualActivityModifier',
  'http://identifiers.org/biomodels.sbo/SBO:0000020': 'inhibitor',
  'http://identifiers.org/biomodels.sbo/SBO:0000206': 'competitiveInhibitor',
  'http://identifiers.org/biomodels.sbo/SBO:0000207': 'nonCompetitiveInhibitor',
  'http://identifiers.org/biomodels.sbo/SBO:0000597': 'silencer',
  'http://identifiers.org/biomodels.sbo/SBO:0000596': 'modifierOfUnknownActivity',
  'http://identifiers.org/biomodels.sbo/SBO:0000459': 'stimulator',
  'http://identifiers.org/biomodels.sbo/SBO:0000013': 'catalyst',
  'http://identifiers.org/biomodels.sbo/SBO:0000460': 'enzymaticCatalyst',
  'http://identifiers.org/biomodels.sbo/SBO:0000461': 'essentialActivator',
  'http://identifiers.org/biomodels.sbo/SBO:0000535': 'bindingActivator',
  'http://identifiers.org/biomodels.sbo/SBO:0000534': 'catalyticActivator',
  'http://identifiers.org/biomodels.sbo/SBO:0000533': 'specificActivator',
  'http://identifiers.org/biomodels.sbo/SBO:0000462': 'nonEssentialActivator',
  'http://identifiers.org/biomodels.sbo/SBO:0000021': 'potentiator',
  'http://identifiers.org/biomodels.sbo/SBO:0000594': 'neutralParticipant',
  'http://identifiers.org/biomodels.sbo/SBO:0000011': 'product',
  'http://identifiers.org/biomodels.sbo/SBO:0000603': 'sideProduct',
  'http://identifiers.org/biomodels.sbo/SBO:0000598': 'promoter',
  'http://identifiers.org/biomodels.sbo/SBO:0000010': 'reactant',
  'http://identifiers.org/biomodels.sbo/SBO:0000336': 'interactor',
  'http://identifiers.org/biomodels.sbo/SBO:0000015': 'substrate',
  'http://identifiers.org/biomodels.sbo/SBO:0000604': 'sideSubstrate'
}

data = {
  "components": [],
  "lines": [],
  "circuit": {
    "id": 1,
    "name": "",
    "description": ""
  },
  "stimulations": [],
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
      if (roleUri in so_dict.keys()):
        component['role'] = so_dict[roleUri]
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
      if sbo_dict[action.types[0]] == 'inhibition':
        inh = {}
        for part in action.participations:
          if part.roles[0] in sbo_dict.keys():
            inh[sbo_dict[part.roles[0]]] = part.displayId
          else:
            inh['other'] = part.displayId
        data['inhibitions'].append(inh)
      elif sbo_dict[action.types[0]] == 'stimulation':
        pro = {}
        for part in action.participations:
          if part.roles[0] in sbo_dict.keys():
            pro[sbo_dict[part.roles[0]]] = part.displayId
          else:
            pro['other'] = part.displayId
        data['stimulations'].append(pro)
      elif sbo_dict[action.types[0]] == 'geneticInteraction':
        com = {
          'reactant': []
        }
        for part in action.participations:
          if part.roles[0] in sbo_dict.keys():
            if sbo_dict[part.roles[0]] == 'reactant':
              com['reactant'].append(part.displayId)
            else:
              com['product'] = part.displayId
        data['combinations'].append(com)

data['circuit']['name'] = filename

json = json.dumps(data)
print(json)