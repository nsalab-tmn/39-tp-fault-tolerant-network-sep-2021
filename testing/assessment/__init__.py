from pyats import aetest
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

def get_trace(exc_info, vars):
    _, _, tb = exc_info
    tb_info = traceback.extract_tb(tb)
    filename, line, func, text = tb_info[-1]
    logger.info('Assertion failed in {} on line {} in function {} in statement {}'.format(filename, line, func, text))
    logger.info('Expected: \r\n' + json.dumps(vars, indent = 2))

def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def go_sleep(testbed, device, action_vars, params):
    logger.info("Going to sleep for " + str(action_vars['seconds'].format_map(params)) + " seconds")
    sleep(int(action_vars['seconds'].format_map(params)))

def verify_output(testbed, device, action_vars, params):
    try:    
        result = testbed.devices[device].execute(action_vars['command'].format_map(params))
        assert_tags(action_vars['assert_tags'], result, action_vars['tags_are_present'], params)
    except AssertionError:
        get_trace(sys.exc_info(), action_vars)
        aetest.steps.Step.failed('Assertion error')
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

