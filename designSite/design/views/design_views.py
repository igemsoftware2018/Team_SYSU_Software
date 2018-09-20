# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from django.http import HttpRequest
from sbol import *

import json
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound,\
    HttpResponseForbidden
from django.contrib import messages

# from design.models import *
from design.models.bio import *
from design.models.user import *


from design.tools.biode import CIR2ODE as cir2

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

import traceback
import logging
logger = logging.getLogger(__name__)

'''
All response contains a status in json
'status' : xxx
1 for success
0 for failed
'''


# Basic design views


role_dict = {
    'promoter': 'Promoter',
    'Promoter': 'Promoter',
    'RBS': 'RBS',
    'CDS': 'CDS',
    'terminator': 'Terminator',
    'Terminator': 'Terminator',
    'process': 'process',
    'ther_DNA': 'User defined',
    'other_DNA': 'User defined',
    'complex': 'Complex',
    'RNA': 'RNA',
    'protein': 'Effector',
    'protein-m': 'Effector',
    'protein-l': 'Effector',
    'protein-I': 'Effector',
    'cell': 'User defined',
    'chemical': 'User defined',
    'material': 'Effector',
    'light': 'Effector',
    'Light': 'Effector',
    'reporter': 'Reporter',
    'composite': 'Composite',
    'generator': 'Generator',
    'inverter': 'Inverter Device',
    'measurement': 'Measurement Device',
    'signalling': 'Signalling Molecule',
    'unknown': 'User defined'
}

TYPE_LIST = ['CDS', 'RBS', 'promoter', 'terminator', 'material',
             'light', 'protein', 'process', 'RNA', 'protein-m', 'protein-l',
             'complex', 'other_DNA', 'composite', 'generator', 'reporter',
             'inverter', 'signalling', 'measurement', 'unknown']


@login_required
def design(request):
    context = {
        'type_list': TYPE_LIST,
        'designID': -1,
        'username': request.user.username
    }
    return render(request, 'design.html', context)

@login_required
def share_design(request):
    '''
    called when a share design is visited.
    /design/share/xxx
    /design/share/realtime/xxx
    '''
    request_user = request.user
    designID = request.path.split('/')[-1]
    isRealtime = request.path.split('/')[-2] == 'realtime'
    logger.debug('share request at %s, realtime = %s ', designID, isRealtime)
    context = {
        'type_list': TYPE_LIST,
        'designID': designID,
        'write_authority': False,
        'username': request.user.username,
        'realtime': isRealtime
    }

    # check whether this id exists
    try:
        circuit = Circuit.objects.get(pk=designID)
        if circuit.Author == request_user:
            return redirect(os.path.join('/design/', designID))
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    except:
        traceback.print_exc()
        logger.error('unknown bugs')
        return HttpResponseNotFound()

    # check authorities
    try:
        authority_query = Authorities.objects.get(User=request_user, Circuit=circuit)
        logger.debug('share authority is <%s> ', authority_query.Authority)
        if authority_query.Authority == 'write':
            context['write_authority'] = True
    except ObjectDoesNotExist:
        return HttpResponseForbidden()
    return render(request, 'design.html', context)

# share related views


@login_required
def users(request):
    '''
    GET method with param:
        username=xxx
    return json:
        'users': [{
            'username': xxx
        }]
    '''
    query_user = request.GET.get('username')
    logger.debug(query_user)
    logger.debug("test")
    if query_user is None or len(query_user) == 0:
        return JsonResponse({'success': False})

    query_set = User.objects.filter(username__contains=query_user)

    users = []
    for x in query_set:
        users.append({'username': x.username})

    return JsonResponse({
        'success': True,
        'users': users
    })


@csrf_exempt
@login_required
def authority(request):
    '''
    POST method with json:
    {
        users: [xxx, xxx(username)],
        circuit: xxx,
        authority: xxx
    }
    return json:
    {
        msg: xxx
    }

    GET method with parameter:
    circuit=xxx
    url:
    "/api/authority?circuit=xxx"
    return json:
    {
        read: [xxx, xxx(username)]
        write: [xxx, xxx(usernam)]
    }

    '''
    if request.method == 'POST':
        users = json.loads(request.POST['users'])
        circuit = Circuit.objects.get(id=request.POST['circuit'])
        auth_str = json.loads(request.POST['authority'])
        Authorities.objects.filter(Circuit=circuit).delete()
        for username in users:
            if username == request.user.username:
                logger.debug('same user %s, skip', username)
                continue
            user = User.objects.get(username=username)
            Authorities.objects.create(
                User=user,
                Circuit=circuit,
                Authority=auth_str
            )
            logger.debug('user <%s> get authority <%s> at circuit <%s>',
                         username, auth_str, circuit.id)
        return JsonResponse({
            'msg': 'Success'
        })
    elif request.method == 'GET':
        designID = request.GET.get('circuit', '')
        try:
            read = []
            write = []
            logger.debug(designID)
            circuit = Circuit.objects.get(pk=designID)
            authorities_query = Authorities.objects.filter(Circuit=circuit)
            for authority in authorities_query:
                if authority.Authority == 'read':
                    read.append(authority.User.username)
                else:
                    write.append(authority.User.username)
            return JsonResponse({
                'read': read,
                'write': write
            })
        except:
            traceback.print_exc()
            return JsonResponse({
                'read': [],
                'write': []
            })
    else:
        logger.error('unknow request method')
        return HttpResponseNotFound()


@login_required
def personal_design(request):
    # the correct way to retrive path elements is split.
    designID = request.path.split('/')[-1]
    designID = int(designID)
    isRealtime = request.path.split('/')[-2] == 'realtime'
    logger.debug('visiting design id=%s, realtime = %s', designID, isRealtime)
    try:
        circuit = Circuit.objects.get(pk=designID)
        user = request.user
        # this design is not construct by this user. forbidden.
        if circuit.Author != user:
            return HttpResponseForbidden()
    except ObjectDoesNotExist:
        # do not exist this id
        return HttpResponseNotFound()
    except:
        # unknown error, in case it occurs
        traceback.print_exc()
        logger.error('unknown bugs')
        return HttpResponseNotFound()
    context = {
        'type_list': TYPE_LIST,
        'designID': designID,
        'username': request.user.username,
        'write_authority': True,
        'realtime': isRealtime
    }
    return render(request, 'design.html', context)


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
    search_target = request.GET.get('flag')
    query_name = request.GET.get('name')
    print(search_target)
    # Params empty
    if query_name is None or len(query_name) == 0:
        return JsonResponse({'success': False})

    query_set = Parts.objects.filter(Name__contains=query_name)

    parts = []
    for x in query_set:
        if search_target[TYPE_LIST.index(str(x.Type))] == '0':
            continue
        if x.IsPublic == 1:
            parts.append({'id': x.id, 'name': "%s" % (x.Name)})
        elif x.Username == request.user.username:
            parts.append(
                {'id': x.id, 'name': "%s (%s)" % (x.Name, x.Username)})
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
        part = Parts.objects.get(Name=query_name)
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
                Username=username,
                IsPublic=False,
                Name=data['name'],
                Description=data['description'],
                Type=data['type'],
                Role=role_dict[data['type']],
                Sequence=data['sequence'],
            )
            for x in data['subparts']:
                SubParts.objects.create(
                    parent=new_part,
                    child=x
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
            part = Parts.objects.get(pk=query_id)
            part_dict = {
                'id': part.id,
                'name': part.Name,
                'description': part.Description,
                'type': part.Type,
                'sequence': part.Sequence,
                'role': part.Role}
            sub_query = SubParts.objects.filter(parent=part)
            part_dict['subparts'] = [{
                'id': x.child.id,
                'name': x.child.Name,
                'description': x.child.Description,
                'type': x.child.Type} for x in sub_query]
            circuit_query = CircuitParts.objects.filter(
                Part=part).values('Circuit').distinct()
            part_dict['works'] = []
            part_dict['papers'] = []
            for x in circuit_query:
                circuit = Circuit.objects.get(pk=x['Circuit'])
                if circuit.works_set.count() > 0:
                    w = circuit.works_set.all()[0]
                    part_dict['works'].append({
                        'year': w.Year,
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
            return JsonResponse({'success': False})


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
        part = Parts.objects.get(pk=query_id)
        query = PartsInteract.objects.filter(parent=part)
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
        return JsonResponse({'success': False})


# Circuit related views
def circuits(request):
    '''
    GET method with param:
        name=xxx
    return json:{
        name: xxx,
        circuits: [{
            ID: xxx,
            Editor: xxx,
            UpdateTime: xxx,
            Comment: xxx
        }]
    }
    '''
    name = json.loads(request.GET['name'])
    circuit_query = Circuit.objects.filter(Name=name)
    circuits = [{
        'ID': x.id,
        'Editor': x.Editor.username if not x.Editor is None else 'None',
        'UpdateTime': x.Update_time,
        'Comment': x.Comment
    } for x in circuit_query]

    return JsonResponse({
        'name': name,
        'circuits': circuits
    })


def circuit(request):
    '''
    GET method with param:
        id=xxx
    return json:{
        status: 1,
        id: xxx,
        name: xxx,
        description: xxx,
        comment: xxx,
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
        },
        chassis: xxx,
        protocol: {
            title: xxx,
            description: xxx,
            steps: [{
                title: xxx,
                body: xxx
            }]
        }
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
        },
        chassis: "xxx",
        circuit: {
            'id': xxx, # circuit id if it's already existing, -1 else
            'name': xxx,
            'description': xxx
            'comment': xxx (exist only when id != -1)
        },
        protocol: {
            'title': xxx,
            'description': xxx,
            'steps': [{
                'title': xxx,
                'body': xxx
            }]
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
            circuit = Circuit.objects.get(id=query_id)
            parts_query = CircuitParts.objects.filter(Circuit=query_id)
            parts = [{'id': x.Part.id, 'cid': x.id, 'name': x.Part.Name,
                      'description': x.Part.Description, 'type': x.Part.Type,
                      'X': x.X, 'Y': x.Y} for x in parts_query]
            line_query = CircuitLines.objects.filter(Start__Circuit=query_id,
                                                     End__Circuit=query_id)
            lines = [{'start': x.Start.id, 'end': x.End.id, 'type': x.Type}
                     for x in line_query]
            devices_query = CircuitDevices.objects.filter(Circuit=query_id)
            devices = [{
                'subparts': [i.id for i in x.Subparts.all()],
                'X':x.X,
                'Y': x.Y} for x in devices_query]
            combines_query = CircuitCombines.objects.filter(Circuit=query_id)
            combines = {x.Father.id: [i.id for i in x.Sons.all()]
                        for x in combines_query}
            chassis = circuit.Chassis.name
            protocol_query = Protocol.objects.get(Circuit=circuit)
            step_query = Step.objects.filter(Father=protocol_query)
            protocol = {
                'title': protocol_query.Title,
                'description': protocol_query.Description,
                'steps': [{
                    'title': x.Title,
                    'body': x.Body,
                } for x in step_query
                ]
            }
            return JsonResponse({
                'status': 1,
                'id': query_id,
                'name': circuit.Name,
                'description': circuit.Description,
                'comment': circuit.Comment,
                'parts': parts,
                'lines': lines,
                'devices': devices,
                'combines': combines,
                'chassis': chassis,
                'protocol': protocol
            })
        except:
            traceback.print_exc()
            return JsonResponse({
                'status': 0})
    elif request.method == 'POST':
        try:
            data = json.loads(request.POST['data'])
            name = data['name']
            new = (data['id'] == -1)
            if name.strip() == '':
                return JsonResponse({
                    'status': -1,
                    'error_msg': "ERROR: Empty Design Name. Fail to Save."
                })
            # Judge if name has been replicated in db
            if Circuit.objects.filter(Name=name).count() > 0 and new:
                return JsonResponse({
                    'status': -1,
                    'error_msg': "Design Name has been used. Please Rename it."
                })
            if not new:
                old_circuit = Circuit.objects.filter(Name=name)[0]
            # New circuit
            circuit = Circuit.objects.create(
                Name=name,
                Description=data['description'] if new else old_circuit.Description,
                Comment="None" if new else data['comment'],
                Author=request.user if new else old_circuit.Author,
                Editor=request.user,
                Chassis=Chassis.objects.get(name=data['chassis'])
            )

            # New protocol and steps
            try:
                protocol = Protocol.objects.create(
                    Circuit=circuit,
                    Title=data['protocol']['title'],
                    Description=data['protocol']['description']
                )
                for idx, step in enumerate(data['protocol']['steps']):
                    Step.objects.create(
                        Father=protocol,
                        Title=step['title'],
                        Body=step['body'],
                        Order=idx
                    )
            except KeyError:
                logger.error('no protocol information found. skip.')

            cids = {}
            for x in data['parts']:
                circuit_part = CircuitParts.objects.create(
                    Part=Parts.objects.get(id=int(x['id'])),
                    Circuit=circuit,
                    X=x['X'] if 'X' in x else 0,
                    Y=x['Y'] if 'Y' in x else 0)
                cids[x['cid']] = circuit_part
            for x in data['lines']:
                try:
                    CircuitLines.objects.get(
                        Start=cids[x['start']],
                        End=cids[x['end']],
                        Type=x['type']
                    )
                except:
                    CircuitLines.objects.create(
                        Start=cids[x['start']],
                        End=cids[x['end']],
                        Type=x['type']
                    )
            for x in data['devices']:
                cd = CircuitDevices.objects.create(Circuit=circuit)
                for i in x['subparts']:
                    cd.Subparts.add(cids[i])
                cd.X = x['X']
                cd.Y = x['Y']
                cd.save()
            for x in data['combines']:
                cd = CircuitCombines.objects.create(Circuit=circuit, Father=x)
                for i in data['combines'][x]:
                    cd.Sons.add(cids[i])
                cd.save()
            return JsonResponse({
                'status': 1,
                'circuit_id': circuit.id})
        except:
            traceback.print_exc()
            return JsonResponse({
                'status': 0
            })
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
    query_set = Circuit.objects.filter(Author=request.user)
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


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def plasmid_data(request):

    with open(os.path.join(BASE_DIR, 'tools/plasmidData.json')) as f:
        return JsonResponse({'data': json.load(f)})

# transform json data to sbol document


@csrf_exempt
def get_sbol_doc(request):
    if request.method == 'POST':
        print(request.POST['data'])
        data = json.loads(request.POST['data'])

        setHomespace('http://sys-bio.org')
        doc = Document()

        roles = {
            # 'RNA': SO_SGRNA,
            'DNA': SO_GENE,
            'RBS': SO_RBS,
            'CDS': SO_CDS,
            'Promoter': SO_PROMOTER,
            'Terminator': SO_TERMINATOR,
            'RNA': 'http://identifiers.org/so/SO:0000356',
            'gene': 'http://identifiers.org/so/SO:0000704',
            'mRNA': 'http://identifiers.org/so/SO:0000234',
            'SGRNA': 'http://identifiers.org/so/SO:0001998',
            'Complex': 'http://identifiers.org/ncit/C47881',
            'operator': 'http://identifiers.org/so/SO:0000057',
            'Effector': 'http://identifiers.org/chebi/CHEBI:35224',
            'Reporter': 'http://identifiers.org/ncit/C41191',
            'Insulator': 'http://identifiers.org/so/SO:0000627',
            'Composite': 'http://identifiers.org/ncit/C61520',
            'Generator': 'http://identifiers.org/ncit/C42770',
            'Signature': 'http://identifiers.org/so/SO:0001978',
            '5\' overhang': 'http://identifiers.org/so/SO:0001932',
            '3\' overhang': 'http://identifiers.org/so/SO:0001933',
            'User defined': 'http://identifiers.org/so/SO:0000804',
            'fivePrimeUtr': 'http://identifiers.org/so/SO:0000204',
            'Assembly scar': 'http://identifiers.org/so/SO:0001953',
            'Protease site': 'http://identifiers.org/so/SO:0001956',
            'engineeredGene': 'http://identifiers.org/so/SO:0000280',
            'Inverter Device': 'http://identifiers.org/ncit/C50010',
            'sequenceFeature': 'http://identifiers.org/so/SO:0000110',
            'sequenceFeature': 'http://identifiers.org/so/SO:0000110',
            'Ribonuclease site': 'http://identifiers.org/so/SO:0001977',
            'Measurement Device': 'http://identifiers.org/ncit/C81182',
            'primer binding site': 'http://identifiers.org/so/SO:0005850',
            'Signalling Molecule': 'http://identifiers.org/chebi/CHEBI:62488',
            'Origin of replication': 'http://identifiers.org/so/SO:0000296',
            'RNA stability element': 'http://identifiers.org/so/SO:0001979',
            'Blunt restriction site': 'http://identifiers.org/so/SO:0001691',
            'Protein stability element': 'http://identifiers.org/so/SO:0001955',
            'Restriction enzyme recognition site': 'http://identifiers.org/so/SO:0001687',
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
                    stimulator_fc = proModule.functionalComponents.create(
                        stimulatorName)
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

                proInteraction = proModule.interactions.create(
                    'stimulation_' + str(index))
                proInteraction.types = SBO_STIMULATION

                stimulator_participation = proInteraction.participations.create(
                    stimulatorName)
                stimulator_participation.roles = SBO_STIMULATOR
                stimulator_participation.participant = pro_fcs[stimulatorName].identity

                other_participation = proInteraction.participations.create(
                    otherName)
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
                    inhibitor_fc = inhModule.functionalComponents.create(
                        inhibitorName)
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

                inhInteraction = inhModule.interactions.create(
                    'inhibition_' + str(index))
                inhInteraction.types = SBO_INHIBITION

                inhibitor_participation = inhInteraction.participations.create(
                    inhibitorName)
                inhibitor_participation.roles = SBO_INHIBITOR
                inhibitor_participation.participant = inh_fcs[inhibitorName].identity

                other_participation = inhInteraction.participations.create(
                    otherName)
                other_participation.roles = components[otherName].roles
                other_participation.participant = inh_fcs[otherName].identity

        # combination
        if 'combinations' in data.keys():
            comModule = ModuleDefinition('combination_module')
            doc.addModuleDefinition(comModule)

            for index, combination in enumerate(data['combinations']):
                comInteraction = comModule.interactions.create(
                    'combination_' + str(index))
                comInteraction.role = SBO_NONCOVALENT_BINDING
                for reactant in combination['reactants']:
                    if not reactant in com_fcs.keys():
                        reactant_fc = comModule.functionalComponents.create(
                            reactant)
                        reactant_fc.definition = components[reactant].identity
                        reactant_fc.access = SBOL_ACCESS_PUBLIC
                        reactant_fc.direction = SBOL_DIRECTION_IN_OUT
                        com_fcs[reactant] = reactant_fc
                    reactant_participation = comInteraction.participations.create(
                        reactant)
                    reactant_participation.roles = SBO_REACTANT
                    reactant_participation.participant = com_fcs[reactant].identity

                product = combination['product']
                if not product in com_fcs.keys():
                    product_fc = comModule.functionalComponents.create(product)
                    product_fc.definition = components[product].identity
                    product_fc.access = SBOL_ACCESS_PUBLIC
                    product_fc.direction = SBOL_DIRECTION_IN_OUT
                    com_fcs[product] = product_fc
                    product_participation = comInteraction.participations.create(
                        product)
                    product_participation.roles = SBO_PRODUCT
                    product_participation.participant = com_fcs[product].identity

        # create sbol document
        circuit_name = data['circuit']['name']
        filename = circuit_name + '.xml'
        result = doc.write(filename)
        print(result)

        response = HttpResponse(open(filename, "rb"), content_type="text/xml")

        if os.path.exists(filename):
            os.remove(filename)

        return response


so_dict = {
    'http://identifiers.org/ncit/C47881': 'Complex',
    'http://identifiers.org/ncit/C61520': 'Composite',
    'http://identifiers.org/ncit/C42770': 'Generator',
    'http://identifiers.org/ncit/C50010': 'Inverter Device',
    'http://identifiers.org/ncit/C81182': 'Measurement Device',
    'http://identifiers.org/ncit/C41191': 'Reporter',
    'http://identifiers.org/so/SO:0000167': 'Promoter',
    'http://identifiers.org/so/SO:0000057': 'operator',
    'http://identifiers.org/so/SO:0000316': 'CDS',
    'http://identifiers.org/so/SO:0000204': 'fivePrimeUtr',
    'http://identifiers.org/so/SO:0000141': 'Terminator',
    'http://identifiers.org/so/SO:0000139': 'RBS',
    'http://identifiers.org/so/SO:0000704': 'gene',
    'http://identifiers.org/so/SO:0000234': 'mRNA',
    'http://identifiers.org/so/SO:0000280': 'engineeredGene',
    'http://identifiers.org/so/SO:0000110': 'sequenceFeature',
    'http://identifiers.org/so/SO:0001998': 'SGRNA',
    'http://identifiers.org/so/SO:0000627': 'Insulator',
    'http://identifiers.org/so/SO:0001977': 'Ribonuclease site',
    'http://identifiers.org/so/SO:0001979': 'RNA stability element',
    'http://identifiers.org/so/SO:0001956': 'Protease site',
    'http://identifiers.org/so/SO:0001955': 'Protein stability element',
    'http://identifiers.org/so/SO:0000296': 'Origin of replication',
    'http://identifiers.org/so/SO:0005850': 'primer binding site',
    'http://identifiers.org/so/SO:0001687': 'Restriction enzyme recognition site',
    'http://identifiers.org/so/SO:0001691': 'Blunt restriction site',
    'http://identifiers.org/so/SO:0001932': '5\' overhang',
    'http://identifiers.org/so/SO:0001933': '3\' overhang',
    'http://identifiers.org/so/SO:0001953': 'Assembly scar',
    'http://identifiers.org/so/SO:0001978': 'Signature',
    'http://identifiers.org/so/SO:0000804': 'User defined',
    'http://identifiers.org/so/SO:0000356': 'RNA',
    'http://identifiers.org/chebi/CHEBI:35224': 'Effector',
    'http://identifiers.org/chebi/CHEBI:62488': 'Signalling Molecule',
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
                if temp.roles:  # components
                    roleUri = temp.roles[0]
                    if (roleUri in so_dict.keys()):
                        component['role'] = so_dict[roleUri]
                    component['id'] = temp.displayId
                    component['name'] = temp.displayId
                    component['version'] = temp.version
                    component['description'] = temp.description
                    sequenceUri = temp.sequences
                    if sequenceUri:
                        component['sequence'] = doc.getSequence(
                            sequenceUri[0]).elements
                    data['components'].append(component)
                else:  # lines
                    line['name'] = temp.displayId
                    line_comp = {}
                    for comp in temp.components:
                        line_comp[str(comp)] = doc.getComponentDefinition(
                            comp.definition).displayId
                    if temp.sequenceConstraints:
                        for index, constraint in enumerate(temp.sequenceConstraints):
                            if (index == 0):
                                line['structure'].append(
                                    line_comp[constraint.subject])
                                line['structure'].append(
                                    line_comp[constraint.object])
                            else:
                                line['structure'].append(
                                    line_comp[constraint.object])
                    else:
                        for comp in temp.components:
                            line['structure'].append(
                                doc.getComponentDefinition(comp.definition).displayId)

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


CHASSIS_FORMAT = [
    '1: Standard',
    '2: Vertebrate Mitochondrial',
    '3: Yeast Mitochondrial',
    '4: Mold, Protozoan, Coelenterate Mitochondrial and Mycoplasma/Spiroplasma',
    '5: Invertebrate Mitochondrial',
    '6: Ciliate Macronuclear and Dasycladacean',
    '9: Echinoderm Mitochondrial',
    '10: Alternative Ciliate Macronuclear',
    '11: Eubacterial',
    '12: Alternative Yeast',
    '13: Ascidian Mitochondrial',
    '14: Flatworm Mitochondrial',
    '15: Blepharisma Nuclear Code'
]


def chassis(request):
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'chassis_format': CHASSIS_FORMAT,
            'chassis': [x.name for x in Chassis.objects.all()]
        })


def get_chassis_info(name, read_format):
    return json.loads(Chassis.objects.filter(name=name)[0].data)[read_format]


import re


@csrf_exempt
def analysis_sequence(request):
    '''
    POST method with json:
    {
        sequence: xxx,
        chassis: xxx,
        mode: xxx
    }
    response with json:
    {
        status: 0 or errno
        CAI: xxx,
        CG: xxx,
        msg: xxx (error msg, ignore me when success)
    }
    '''
    if request.method == 'POST':
        seq = request.POST['sequence']
        chassis = request.POST['chassis']
        chassis_format = request.POST['mode']

        if not re.match('^[atcgATCG]*$', seq):
            return JsonResponse({
                'status': 1,
                'msg': 'Error: The sequence include invalid characters. Only A, C, T, G, a, c, t, g are allowed'
            })
        if len(seq) % 3 != 0 or len(seq) == 0:
            return JsonResponse({
                'status': 2,
                'msg': 'Error: the length of the sequence is zero or is not dividable by three. Can not decode'
            })

        # for CG
        cg_num = sum(map(lambda ch: 1 if ch in 'cgCG' else 0, seq))
        CG = cg_num / len(seq) * 100

        # for CAI
        def dna2rna(ch):
            if ch in 'aA':
                return 'U'
            if ch in 'tT':
                return 'A'
            if ch in 'cC':
                return 'G'
            if ch in 'gG':
                return 'C'
            raise Exception('invalid dna seq format {}'.format(ch))
        rna = list(map(dna2rna, seq.strip()))
        # break every 3 elements into groups
        # rna_codon = ['XXX', 'XXX', 'XXX']
        rna_codon = [''.join(rna[i:i+3]) for i in range(0, len(rna), 3)]
        logger.debug("rna_codon %s", rna_codon)
        chassis_codon_table = json.loads(
            Chassis.objects.get(name=chassis).data)  # get the json
        # get the mode
        chassis_codon_table = chassis_codon_table[chassis_format]

        max_frequency = {}  # map amino_acid(str) to frequency(float)
        codon2amino_acid = {}  # map codon(str) to amino_acid(str)
        codon2frequency = {}  # map codon(str) to frequency(float)
        # init the above dicts
        for item in chassis_codon_table:
            codon = item['codon']
            amino_acid = item['amino_acid']
            f = item['frequency']
            if max_frequency.get(amino_acid) is None:
                max_frequency[amino_acid] = float(f)
            else:
                max_frequency[amino_acid] = max(
                    max_frequency[amino_acid], float(f))
            codon2amino_acid[codon] = amino_acid
            codon2frequency[codon] = float(f)
        logger.debug('max_frequency %s', max_frequency)
        logger.debug('codon2amino_acid %s ', codon2amino_acid)
        logger.debug('codon2frequency %s ', codon2frequency)

        # calculate CAI
        weights = []
        for codon in rna_codon:
            f = codon2frequency[codon]
            amino = codon2amino_acid[codon]
            max_f = max_frequency[amino]
            weights.append(f/max_f)

        def product(iter):
            acc = 1
            for i in iter:
                acc *= i
            return acc
        CAI = product(weights) ** (1/len(weights)) * 100
        logger.debug('CAI %s', CAI)
        logger.debug('CG %s', CG)

        return JsonResponse({
            'status': 0,
            'CAI': CAI,
            'CG': CG,
            'msg': 'success'
        })

@login_required
def api_real_time(request):
    '''
    /api/realtime/xxx
    GET
    {
        'design_data': 'xxx' // (not used in backend) JSON.parse() -> design.design,
        'first_time': 'xxx' // json.loads -> boolean
    }
    POST
    {
        'design_data': 'xxx' // (not used in backend) design.design -> JSON.stringify
        'first_time': 'xxx' // boolean -> JSON.stringify
    }
    '''
    if request.method == 'GET':
        designID = request.path.split('/')[-1]
        logger.debug("api real time GET, designID = %s", designID)
        circuit = Circuit.objects.get(pk=designID)
        try:
            realtime_design_query = RealtimeDesign.objects.get(Circuit=circuit)
            design_query = realtime_design_query.Design
            return JsonResponse({
                'design_data': design_query
            })
        except ObjectDoesNotExist:
            return JsonResponse({})
        return JsonResponse({})
    elif request.method == 'POST':
        design_post = request.POST['design_data']
        is_first_time = json.loads(request.POST['first_time'])
        designID = request.path.split('/')[-1]
        logger.debug("api real time POST at designID %s", designID)
        logger.debug('new design is %s', design_post)
        circuit = Circuit.objects.get(pk=designID) # must successful.
        # testing write authority
        if request.user != circuit.Author:
            try:
                auth_query = Authorities.objects.get(
                    User=request.user,
                    Circuit=circuit
                )
                auth = auth_query.Authority
                if (auth != 'write'):
                    return JsonResponse({'errno':1, 'msg': 'not right to write'})
            except ObjectDoesNotExist:
                return JsonResponse({'errno':1, 'msg': 'not right to access'})
        # alter design.design json in db
        try:
            rtd = RealtimeDesign.objects.get(Circuit=circuit)
            if (not is_first_time):
                rtd.Design = design_post
                rtd.save()
                logger.debug('not first time. update')
            else:
                logger.debug('first time. skip to update')
        except ObjectDoesNotExist:
            RealtimeDesign.objects.create(
                Circuit=circuit,
                Design=design_post
            )
        return JsonResponse({
            'msg': 'hello'
        })
