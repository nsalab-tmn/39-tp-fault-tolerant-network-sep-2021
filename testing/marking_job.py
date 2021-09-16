import yaml
import json
from pyats.easypy import run
from pyats.easypy import Task
from genie import testbed
from yamlinclude import YamlIncludeConstructor
from argparse import ArgumentParser
from assessment import update_dict, generate_testbed, get_cml_lab
import os


def main(runtime):
    parser = ArgumentParser(description='pyATS job wrapper')
    parser.add_argument('--marking-file', dest='DATAFILE', required=False, default='marking.yaml', help='Marking datafile')
    parser.add_argument('--include-basedir', dest='BASEDIR', required=False, default='./testcases.d', help='Testcases basedir')
    parser.add_argument('--internal-params', dest='PARAMS', required=False, default='params.yaml', help='Internal parameters')
    parser.add_argument('--lab-id', dest='LAB', required=True, default='15f2e2', help='CML lab id')
    parser.add_argument('--unit-test', dest='UT', required=False, default='ut.py', help='Unit test script')
    args = parser.parse_args()
    
    try:
        YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader, base_dir=args.BASEDIR)        
        with open(args.DATAFILE) as f:
            df = yaml.load(f, Loader=yaml.FullLoader)        
        with open(args.PARAMS) as f:
            params = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        print('Exception occured: ' + str(e))
        exit(1)
    
    # tasks = []
    # seq = 0
    # for prefix in tfd:
    # update_dict(params, tfd[prefix])
    # setenv(params)
    lab = get_cml_lab(os.environ['CML_HOST'], os.environ['CML_USER'], os.environ['CML_PASSWORD'], False, args.LAB)
    generate_testbed(lab, filename='testbed.yaml', update='testbed-params.yaml')
    tb = testbed.load('testbed.yaml') 
    # tasks.append(Task(
    task = Task(
        testscript = args.UT,
        testbed=tb,
        datafile=df,
        runtime = runtime,
        taskid = args.LAB,
        params = params,
        lab = lab)
    task.start()
    task.wait()
    # tasks[seq].start()
    # tasks[seq].wait()
        # seq += 1
    
