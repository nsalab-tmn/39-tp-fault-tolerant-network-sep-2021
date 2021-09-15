from pyats import aetest
import dns.resolver 
import ipaddress
import httpx
import os
from time import sleep
import logging
import collections.abc
logger = logging.getLogger(__name__)
import sys
import traceback
from nested_lookup import nested_lookup
import json
import yaml
import io

###CML specific

from virl2_client import ClientLibrary 

def validate_web_response(testbed, device, action_vars, params): 
    try:
        verify = 'assert_cert' in action_vars.keys() and action_vars['assert_cert']
        client = httpx.Client(verify = verify)             
        query_params = httpx.QueryParams() 
        method = 'GET'
        content = None
        if 'query_params' in action_vars.keys():
            qp = kv_to_dict(action_vars['query_params'], params)
            query_params = query_params.merge(qp)
        if 'method' in action_vars.keys():
            method = action_vars['method']
        if 'content' in action_vars.keys():
            c = kv_to_dict(action_vars['content'], params)
            content = json.dumps(c)
            #content = str(c).replace('\'','"')
            #content = action_vars['content'].format_map(params)
        
        request = httpx.Request(method = method,
            url = action_vars['name'].format_map(params),
            content = content,
            params = query_params)        
        if 'headers' in action_vars.keys():
            h = kv_to_dict(action_vars['headers'], params)
            request.headers.update(h)
        
        response = client.send(request)

        if 'set_params' in action_vars.keys():
            j = response.json()            
            if len(j.keys()) > 0 and len(action_vars['set_params']) > 0:
                for seq in range(len(action_vars['set_params'])):
                    key = action_vars['set_params'][seq]
                    val = get_first_value(j, key)
                    params[key] = val
        if 'assert_code' in action_vars.keys():
            assert response.status_code == action_vars['assert_code']
        if 'assert_code_range' in action_vars.keys():
            assert response.status_code >= action_vars['assert_code_range']['min']
            assert response.status_code <= action_vars['assert_code_range']['max']
        if 'assert_redirect' in action_vars.keys() and action_vars['assert_redirect']:
            assert len(response.history) > 0
        if 'assert_content' in action_vars.keys():
            for content in action_vars['assert_content']:
                assert content in response.text
        if 'assert_json' in action_vars.keys():
            j = response.json()
            for seq in range(len(action_vars['assert_json'])):
                values = get_all_values(j, action_vars['assert_json'][seq]['key'])
                assert action_vars['assert_json'][seq]['value'] in values
        if 'assert_json_answer' in action_vars.keys():
            j = response.json()
            case = False
            to_str = True
            for seq in range(len(action_vars['assert_json_answer'])):
                key = action_vars['assert_json_answer'][seq]['key']
                answer = get_first_value(j, key)
                correct_answer = action_vars['assert_json_answer'][seq]['value']
                if 'to_str' in action_vars['assert_json_answer'][seq].keys():
                    to_str = action_vars['assert_json_answer'][seq]['to_str']
                    if 'case' in action_vars['assert_json_answer'][seq].keys():
                        case = action_vars['assert_json_answer'][seq]['case']
                if to_str:
                    answer = str(answer)
                    correct_answer = str(correct_answer)
                    if not case:
                        answer = answer.lower()
                        correct_answer = correct_answer.lower()
                assert correct_answer in answer
    except AssertionError:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed('Response: ' + response.text)
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def get_trace(exc_info, vars):
    _, _, tb = exc_info
    tb_info = traceback.extract_tb(tb)
    filename, line, func, text = tb_info[-1]
    logger.info('Assertion failed in {} on line {} in function {} in statement {}'.format(filename, line, func, text))
    logger.info('Expected: ' + str(vars))

def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def setenv(params):
    for p in params:
        os.environ[p.replace("-","_")] = str(params[p])

def get_all_values(dictionary, key):
    values = []
    generator = item_generator(dictionary, key)
    for v in generator:
        values.append(v)
    return values

def get_first_value(dictionary, key):
    generator = item_generator(dictionary, key)
    for v in generator:
        return(v)

def go_sleep(testbed, device, action_vars, params):
    logger.info("Going to sleep for " + str(action_vars['seconds'].format_map(params)) + " seconds")
    sleep(int(action_vars['seconds'].format_map(params)))

def kv_to_dict(kvdict, params): 
    d = {}
    for seq in kvdict: 
        if type(seq['key']) == str: k = seq['key'].format_map(params) 
        else: k = seq['key'] 
        if type(seq['value']) == str: v = seq['value'].format_map(params) 
        else: v = seq['value'] 
        d[k] = v 
        # d[str(seq['key']).format_map(params)] = str(seq['value']).format_map(params) 
        #append({str(kvdict[seq]['key']).format_map(params): str(kvdict[seq]['value']).format_map(params)}) 
    return d 

def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)            
    
def validate_dns_record(testbed, device, action_vars, params):
    resolver = dns.resolver.Resolver()
    try:
        nameservers = nslookup(action_vars['name'].format_map(params))
        resolver.nameservers = ntoa(nameservers)
        answer = resolver.resolve(action_vars['name'].format_map(params), action_vars['record_type'])
        assert len(answer.response.answer[0]) >= action_vars['min_records']
        for seq in range(action_vars['min_records']):
            assert ipaddress.ip_address(str(answer.rrset[seq])).is_private == action_vars['is_private']
    except AssertionError:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed('Response: ' + str(answer))
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def nslookup(domain):
    result = []
    name = dns.name.from_text(domain)
    answer = dns.resolver.resolve(name, 'NS', raise_on_no_answer=False)
    if answer.rrset is not None:
        for set in answer.rrset:
            result.append(str(set))      
        return result
    else:    
        return nslookup(str(name.parent()))

def ntoa(names):
    try:
        addr = []
        for seq in range(len(names)): 
            answer = dns.resolver.resolve(names[seq]) 
            addr.append(str(answer.rrset[0])) 
    except Exception as e:
        logger.info("Exception occured:" + e.msg)
    finally:
        return addr

def set_params(testbed, device, action_vars, params): 
    try:
        for var in action_vars:
            params[var['key']] = var['value']
        return params
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def find_interface(testbed, device, action_vars, params): 
    try:
        command = "show ip route " + action_vars['network'].format_map(params) + " | include \*"
        result = testbed.devices[device].execute(command)
        if result is not None:        
            params[action_vars['param']] = result.split(' via ').pop()
        return params
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def verify_output(testbed, device, action_vars, params):
    try:    
        result = testbed.devices[device].execute(action_vars['command'].format_map(params))
        assert_tags(action_vars['assert_tags'], result, action_vars['tags_are_present'], params)
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def run_shell_commands(testbed, device, action_vars, params):
    try:
        results = ''
        for seq in range(len(action_vars['commands'])):
            results = results + testbed.devices[device].execute(action_vars['commands'][seq].format_map(params), timeout=300)
        if 'set_param' in action_vars.keys() and action_vars['set_param'] is not None:
            params[action_vars['set_param']] = results
        return results
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def config(testbed, device, action_vars, params):
    try:
        for seq in range(len(action_vars['commands'])): 
            action_vars['commands'][seq] = action_vars['commands'][seq].format_map(params) 
        result = testbed.devices[device].configure(action_vars['commands'])
        return result
    except Exception as e:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed("Exception occured:" + str(e))

def assert_tags(reference_tags, output, present, params):
    if present:
        for tag in reference_tags:
            assert tag.format_map(params) in output
    else:
        for tag in reference_tags:
            assert tag not in output
    return True


#######CML specific

def get_cml_lab(host, username, password, verify, lab_id):
    try:
        client = ClientLibrary("https://" + host, username, password, verify) 
        return client.join_existing_lab(lab_id)
    except Exception as e:
        get_trace(sys.exc_info(), e)

def generate_testbed(lab = None, filename='testbed.yaml', update = None):
    try:
        tb_stream = io.StringIO(lab.get_pyats_testbed())
        tb_yaml = yaml.load(tb_stream, Loader=yaml.FullLoader)
        if update != None:
            with open(update) as f:
                update_yaml = yaml.load(f, Loader=yaml.FullLoader)
            tb_yaml = update_dict(tb_yaml, update_yaml)
        with open(filename, 'w') as outfile:
            yaml.dump(tb_yaml, outfile, default_flow_style=False)
    except Exception as e:
        get_trace(sys.exc_info(), e)

def set_link_condition(testbed, device, action_vars, params):
    try:
        node = params['lab'].get_node_by_label(action_vars['device'])
        intf = node.get_interface_by_label(action_vars['interface'])
        link = intf.links()[0]
        
        if action_vars['state'] == 'start':
            if link.state == 'STARTED':
                logger.info(action_vars['device'] + " interface " + action_vars['interface'] + " link is already started")
            else:
                logger.info("Starting link: " + link.node_a.label + ":" + link.interface_a.label + "<->" + link.interface_b.label + ":" + link.node_b.label)
                link.start()
        elif action_vars['state'] == 'stop':
            if link.state == 'STOPPED':
                logger.info(action_vars['device'] + " interface " + action_vars['interface'] + " link is already stopped")
            else:
                logger.info("Stopping link: " + link.node_a.label + ":" + link.interface_a.label + "<->" + link.interface_b.label + ":" + link.node_b.label)
                link.stop()          

    except Exception as e:
        get_trace(sys.exc_info(), e)

