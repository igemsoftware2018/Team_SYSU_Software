# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from django.http import HttpRequest
from sbol import *

import json
from django.http import HttpResponse, JsonResponse

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
    parts = [{
        'id': x.id,
        'name': x.Name} for x in query_set]
    parts = parts[:50]

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
            data = json.loads(request.POST['data'])
            new_part = Parts.objects.create(
                Name = data['name'],
                Description = data['description'],
                Type = data['type']
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
                'type': part.Type}
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
                        Type = x['type'] # TODO change promotion to stimulation
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

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_sbol_doc(request):
    if request.method == 'POST':
        data = json.loads(request.POST['data'])
        # data = json.load(test)

        setHomespace('http://sys-bio.org')
        doc = Document()

        roles = {
            'DNA': SO_GENE,
            'RNA': SO_SGRNA,
            'Promoter': SO_PROMOTER,
            'RBS': SO_RBS,
            'CDS': SO_CDS,
            'Terminator': SO_TERMINATOR
        }


        # test = open("data.json", encoding='utf-8')
        # data = json.load(test)

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

        response = HttpResponse(open(filename,"rb"),content_type="text/xml")

        if os.path.exists(filename):
            os.remove(filename)

        return response
