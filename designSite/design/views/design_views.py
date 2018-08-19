# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from django.http import HttpRequest
from sbol import *

import json
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

# from design.models import *
from design.models.bio import *
from design.models.user import *


from design.tools.biode import CIR2ODE as cir2

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist

import traceback
import logging
logger = logging.getLogger('design.views')

'''
All response contains a status in json
'status' : xxx
1 for success
0 for failed
'''


# Basic design views

@login_required
def design(request):
    return render(request, 'design.html')

def test(request):
    return render(request, 'test.html')

# Favorites related views

def get_favorite(request):
    '''
    GET method with no param
    return json:
        'circuits': [{
            'id': xxx,
            'Name': xxx,
            'Description': xxx,
            'Author': xxx(id)
        }]
    '''
    query_set = UserFavorite.objects.filter(user = request.user)
    favorites_circuit = [{
        'id': x.circuit.id,
        'name': x.circuit.Name,
        'description': x.circuit.Description,
        'author': x.circuit.Author.id if x.circuit.Author != None else None
        } for x in query_set]
    query_set = FavoriteParts.objects.filter(user = request.user)
    favorites_part = [{
        'id': x.part.id,
        'name': x.part.secondName,
        'BBa': x.part.Name,
        'type': x.part.Type,
        'safety': x.part.Safety
        } for x in query_set]
    return JsonResponse({
        'status': 1,
        'circuits': favorites_circuit,
        'parts': favorites_part
    })

def tag_favorite(request):
    '''
    POST method with json:
        'circuit_id': xxx, # id of circuit, make sure this circuit is saved
        'tag': 0 for cancel favorite, 1 for tag favorite
    return json:
        status: 0 or 1
    '''
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        try:
            circuit = Circuit.objects.get(pk = data['circuit_id'])
            if data['tag'] == 1:
                if not UserFavorite.objects.filter(user = request.user, circuit = circuit).exists():
                    UserFavorite.objects.create(circuit = circuit, user = request.user)
            else:
                UserFavorite.objects.get(user = request.user, circuit = circuit).delete()
            return JsonResponse({
                'success': True
            })
        except:
            return JsonResponse({
                'success': False
            })

def part_favorite(request):
    '''
    POST method with json:
        'part_id': xxx, # id of part
        'tag': 0 for cancel favorite, 1 for tag favorite
    return json:
        status: 0 or 1
    '''
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        try:
            part = Parts.objects.get(pk = data['part_id'])
            if data['tag'] == 1:
                if not FavoriteParts.objects.filter(user = request.user, part = part).exists():
                    FavoriteParts.objects.create(part = part, user = request.user)
            else:
                FavoriteParts.objects.get(user = request.user, part = part).delete()
            return JsonResponse({
                'success': True
            })
        except:
            return JsonResponse({
                'success': False
            })


# Part related views
@login_required
def parts(request):
    '''
    GET method with param:
        name=xxx
    return json:
        'parts': [{
            'id': xxx,
            'name': xxx
        }]
    '''
    query_name = request.GET.get('name')
    # Params empty
    if query_name is None or len(query_name) == 0:
        return JsonResponse({ 'success': False })

    query_set = Parts.objects.filter(Name__contains = query_name)

    parts = []
    for x in query_set:
        if x.IsPublic == 0 or x.Useranme == request.user.username:
            parts.append({'id': x.id, 'name': "%s (%s)" % (x.Name, x.Username)})
        if len(parts) > 50: 
            break


    return JsonResponse({
        'success': True,
        'parts': parts
    })

def plasm_part(request):
    '''
    GET method with param:
        name=xxx
    return json:
        'seq': xxx
    '''
    query_name = request.GET.get('name')
    try:
        part = Parts.objects.get(Name = query_name)
        return JsonResponse({
            'success': True,
            'seq': part.Sequence
        })
    except:
        return JsonResponse({
            'success': False,
            'seq': 'No sequence found! Try another part name.'
        })

@login_required
def part(request):
    '''
    GET method with param:
        id=xxx
    return json:
        part: {
            'id': xxx,
            'name': xxx,
            'description': xxx,
            'type': xxx,
            'subparts': [
                {
                    'id': xxx,
                    'name': xxx,
                    'description': xxx,
                    'type': xxx
                }
            ],
            'works': [{
                'year': xxx,
                'teamname': xxx,
                'id': xxx}],
            'papers': [
                'Titla': xxx,
                'DOI': xxx,
                'id': xxx,
                'Authors' : xxx
            ]
        }
    '''
    if request.method == 'POST':
        try:
            username = request.user.username
            data = json.loads(request.POST['data'])
            new_part = Parts.objects.create(
                Username = username,
                IsPublic = False,
                Name = data['name'],
                Description = data['description'],
                Type = data['type'], 
                Role = data['role'],
                Sequence = data['sequence'],
            )
            for x in data['subparts']:
                SubParts.objects.create(
                    parent = new_part,
                    child = x
                )
            return JsonResponse({
                'success': True,
                'id': new_part.id
            })
        except:
            return JsonResponse({
                'success': False
            })
    else:
        try:
            query_id = request.GET.get('id')
            part = Parts.objects.get(pk = query_id)
            part_dict = {
                'id': part.id,
                'name': part.Name,
                'description': part.Description,
                'type': part.Type,
                'sequence': part.Sequence,
                'role': part.Role}
            sub_query = SubParts.objects.filter(parent = part)
            part_dict['subparts'] = [{
                'id': x.child.id,
                'name': x.child.Name,
                'description': x.child.Description,
                'type': x.child.Type} for x in sub_query]
            circuit_query = CircuitParts.objects.filter(Part = part).values('Circuit').distinct()
            part_dict['works'] = []
            part_dict['papers'] = []
            for x in circuit_query:
                circuit = Circuit.objects.get(pk = x['Circuit'])
                if circuit.works_set.count() > 0:
                    w = circuit.works_set.all()[0]
                    part_dict['works'].append({
                            'year' : w.Year,
                            'teamname': w.Teamname,
                            'id': w.TeamID
                        })
                elif circuit.papers_set.count() > 0:
                    w = circuit.papers_set.all()[0]
                    part_dict['papers'].append({
                            'title': w.Title,
                            'DOI': w.DOI,
                            'authors': w.Authors,
                            'id': w.id
                        })

            part_dict['success'] = True
            return JsonResponse(part_dict)
        except:
            traceback.print_exc()
            return JsonResponse({ 'success': False })

def interact(request):
    '''
    GET /api/interact?id=xxx:
    return json:
        parts:[{
            'id': xxx,
            'name': xxx,
            'type': xxx,
            'description': xxx,
            'interactType': xxx,
            'score': xxx
        },...]
    '''
    try:
        query_id = request.GET.get('id')
        part = Parts.objects.get(pk = query_id)
        query = PartsInteract.objects.filter(parent = part)
        parts = [
            {
                'id': x.child.id,
                'BBa': x.child.Name,
                'name': x.child.secondName,
                'type': x.child.Type,
                'description': x.child.Description,
                'interactType': x.InteractType,
                'score': x.Score
            } for x in query]

        return JsonResponse({
                'parts': parts
            })
    except:
        raise
        return JsonResponse({ 'success': False })


# Circuit related views

def circuit(request):
    '''
    GET method with param:
        id=xxx
    return json:
        parts: [{
            'id': xxx, # id of part on Parts table
            'cid': xxx, # id for circuit, used in lines
            'Name': xxx,
            'Description': xxx,
            'Type': xxx,
            'X': xxx, # position in canvas
            'Y': xxx,}
        ],
        lines: [{
            'Start': xxx,    # part cid
            'End': xxx,  # part cid
            'Type': xxx, # connection type}
        ],
        devices: [
            {
                'subparts': [xx, xx, xx], # cid
                'x': xxx,
                'y': xxx
            }
        ],
        combines: {
            x: [x, x, x], # combines dict, x is cid
        }

    POST method with json:
    {
        parts: [{
            'id': xxx,
            'cid': xxx, # cid generated by yourself
            'X': xxx,
            'Y': xxx
        }],
        lines: [{
            'start': xxx, # cid defined by yourself
            'end': xxx,
            'type': xxx
        }],
        devices: [
            {
                'subparts': [xx, xx, xx], # cid
                'x': xxx,
                'y': xxx
            }
        ],
        combines: {
            x: [x, x, x] # see above api
        }
        circuit: {
            'id': xxx, # circuit id if it's already existing, -1 else
            'name': xxx,
            'description': xxx
        }
    }
    response with json:
    {
        status: 0 for error, 1 for success.
        circuit_id: xxx # id for saved circuit.
    }
    '''
    if request.method == 'GET':
        try:
            query_id = request.GET.get('id')
            circuit = Circuit.objects.get(id = query_id)
            parts_query = CircuitParts.objects.filter(Circuit = query_id)
            parts = [{'id': x.Part.id, 'cid': x.id, 'name': x.Part.Name,
                'description': x.Part.Description, 'type': x.Part.Type,
                'X': x.X, 'Y': x.Y} for x in parts_query]
            line_query = CircuitLines.objects.filter(Start__Circuit = query_id, \
                    End__Circuit = query_id)
            lines = [{'start': x.Start.id, 'end': x.End.id, 'type': x.Type} \
                    for x in line_query]
            devices_query = CircuitDevices.objects.filter(Circuit = query_id)
            devices = [{
                'subparts': [i.id for i in x.Subparts.all()],
                'X':x.X,
                'Y': x.Y} for x in devices_query]
            combines_query = CircuitCombines.objects.filter(Circuit = query_id)
            combines = {x.Father.id: [i.id for i in x.Sons.all()] for x in combines_query}
            return JsonResponse({
                'status': 1,
                'id': query_id,
                'name': circuit.Name,
                'description': circuit.Description,
                'parts': parts,
                'lines': lines,
                'devices': devices,
                'combines': combines})
        except:
            traceback.print_exc()
            return JsonResponse({
                'status': 0})
    elif request.method == 'POST':
        try:
            data = json.loads(request.POST['data'])
            new = data['circuit']['id'] == -1
            try:
                circuit = Circuit.objects.get(pk = data['circuit']['id'])
                logger.error(str(data['circuit']))
                if (not request.user.is_admin) and circuit.Author != request.user:
                    new = True
                else:
                    new = False
            except:
                new = True
            if new:
                # new circuit
                circuit = Circuit.objects.create(
                        Name = data['circuit']['name'],
                        Description = data['circuit']['description'],
                        Author = request.user)
            else:
                # existing circuit
                circuit = Circuit.objects.get(pk = data['circuit']['id'])
                circuit.Name = data['circuit']['name']
                circuit.Description = data['circuit']['description']
                circuit.Author = request.user
                circuit.save()
                # delete existing circuit part, device
                for x in CircuitParts.objects.filter(Circuit = circuit):
                    x.delete()
                for x in CircuitDevices.objects.filter(Circuit = circuit):
                    x.delete()
                for x in CircuitCombines.objects.filter(Circuit = circuit):
                    x.delete()

            cids = {}
            for x in data['parts']:
                circuit_part = CircuitParts.objects.create(
                        Part = Parts.objects.get(id = int(x['id'])),
                        Circuit = circuit,
                        X = x['X'] if 'X' in x else 0,
                        Y = x['Y'] if 'Y' in x else 0)
                cids[x['cid']] = circuit_part
            for x in data['lines']:
                try:
                    CircuitLines.objects.get(
                        Start = cids[x['start']],
                        End = cids[x['end']],
                        Type = x['type']
                    )
                except:
                    CircuitLines.objects.create(
                        Start = cids[x['start']],
                        End = cids[x['end']],
                        Type = x['type']
                    )
            for x in data['devices']:
                cd = CircuitDevices.objects.create(Circuit = circuit)
                for i in x['subparts']:
                    cd.Subparts.add(cids[i])
                cd.X = x['X']
                cd.Y = x['Y']
                cd.save()
            for x in data['combines']:
                cd = CircuitCombines.objects.create(Circuit = circuit, Father = x)
                for i in data['combines'][x]:
                    cd.Sons.add(cids[i])
                cd.save()
            return JsonResponse({
                    'status': 1,
                    'circuit_id': circuit.id})
        except:
            traceback.print_exc()
            return JsonResponse({
                'status': 0})
    else:
        return JsonResponse({
            'status': 0})

def get_saves(request):
    '''
    GET method with no param
    return json:
        'circuits': [{
            'id': xxx,
            'Name': xxx,
            'Description': xxx,
            'Author': xxx(id)
        }]
    '''
    query_set = Circuit.objects.filter(Author = request.user)
    saves = [{
        'id': x.id,
        'name': x.Name,
        'description': x.Description,
        'author': x.Author.id if x.Author != None else None
        } for x in query_set]
    return JsonResponse({
            'status': 1,
            'circuits': saves})


import numpy as np

def simulation(request):
    '''
    POST /api/simulation
    param:
        n * n list
    return:
        time: [] a list of time stamp of length m
        result: m * n list, result[m][n] means at time m, the concentration of
            n th material
    '''
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        time, result = cir2(data, np.zeros(len(data)))
        return JsonResponse({
            'status': 1,
            'time': time.tolist(),
            'result': result.tolist()
        })
    return 0

def max_safety(request):
    '''
    GET /api/max_safety
    param:
        ids: array of int (as part id)
    return:
        maximum safety in these parts
    '''
    if request.method == 'GET':
        try:
            data = json.loads(request.GET['ids'])
            parts = list(map(lambda i: Parts.objects.get(id = i), data))
            # TODO:
            # 以下代码可以防止一个异常抛出。先检验parts是否为空。为空时返回-1,代表unknown
            if parts == []:
                return JsonResponse({ 'status': 1, 'max_safety': -1}) 
            max_safety_part = max(parts, key = lambda p: p.Safety)
            return JsonResponse({
                'status': 1,
                'max_safety': max_safety_part.Safety
            })
        except:
            traceback.print_exc()
            return JsonResponse({
                'status': 0
            })
    else:
        return JsonResponse({
            'status': 0
        })

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def plasmid_data(request):
    
    with open(os.path.join(BASE_DIR, 'tools/plasmidData.json')) as f:
        return JsonResponse({ 'data': json.load(f) })

# transform json data to sbol document
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_sbol_doc(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        setHomespace('http://sys-bio.org')
        doc = Document()

        roles = {
            'DNA': SO_GENE,
            'RNA': SO_SGRNA,
            'Promoter': SO_PROMOTER,
            'RBS': SO_RBS,
            'CDS': SO_CDS,
            'Terminator': SO_TERMINATOR,
            'sequenceFeature': 'http://identifiers.org/so/SO:0000110',
        }

        activity = Activity(data['circuit']['name'])
        activity.displayId = data['circuit']['name']
        activity.description = data['circuit']['description']
        doc.addActivity(activity)

        # load components
        components = {}
        for component in data['components']:
            temp = ComponentDefinition(component['name'])
            temp.roles = roles[component['role']]
            temp.description = component['description']
            temp.sequence = Sequence(component['name'], component['sequence'])
            components[component['name']] = temp
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

        # stimulation
        if 'stimulations' in data.keys():
            proModule = ModuleDefinition('stimulation_module')
            doc.addModuleDefinition(proModule)

            for index, stimulation in enumerate(data['stimulations']):
                stimulatorName = stimulation['stimulator']
                otherName = stimulation['other']
                
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

                proInteraction = proModule.interactions.create('stimulation_' + str(index))
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

        response = HttpResponse(open(filename,"rb"),content_type="text/xml")

        if os.path.exists(filename):
            os.remove(filename)

        return response


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

@csrf_exempt
def get_sbol_json(request):
    if request.method == 'POST':
        doc = Document()
        doc.readString(request.POST['data'])

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
                    if temp.sequenceConstraints:
                        for index, constraint in enumerate(temp.sequenceConstraints):
                            if (index == 0):
                                line['structure'].append(line_comp[constraint.subject])
                                line['structure'].append(line_comp[constraint.object])
                            else:
                                line['structure'].append(line_comp[constraint.object])
                    else:
                        for comp in temp.components:
                            line['structure'].append(doc.getComponentDefinition(comp.definition).displayId)

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

        jsonData = json.dumps(data)
        return JsonResponse({
            'status': 1,
            'data': jsonData
        })