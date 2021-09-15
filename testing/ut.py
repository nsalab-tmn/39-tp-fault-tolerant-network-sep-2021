from pyats import aetest
from assessment import * 


# define a common setup section by inherting from aetest
class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, testbed, steps, params):
        params['lab'] = get_cml_lab(os.environ['CML_HOST'], os.environ['CML_USER'], os.environ['CML_PASSWORD'], False, self.parent.uid)
        for device in testbed.devices:
            with steps.start('Connecting to %s' % device):
                try:
                    if device not in params['skip_connections'] and device != 'dummy':
                        testbed.devices[device].connect()
                        if testbed.devices[device].connections[next(iter(testbed.devices[device].connections))].get('proxy') is not None: 
                            hostname = testbed.devices[device].execute({'linux': 'hostname'}.get(testbed.devices[device].os, 'show version | i uptime'))
                            if testbed.devices[device].alias not in hostname:
                                aetest.steps.Step.skipped('Device is not reachable over proxy, skipping')     
                    else:
                        aetest.steps.Step.skipped('Params: skipping connection to ' + device)     
                except Exception as e:
                    logger.info("Exception occured:" + e.msg)
                    aetest.steps.Step.skipped('Connection error, skipping')
  
# define common cleanup after all tests are finished
class CommonCleanup(aetest.CommonCleanup):
    
    @aetest.subsection
    def disconnect_from_devices(self, testbed, steps):
        for device in testbed.devices:
            with steps.start('Disconnecting from %s' % device):
                if testbed.devices[device].connected:
                    testbed.devices[device].disconnect()                                     
                else:
                    aetest.steps.Step.skipped('Device was not connected')

# basic workflow to process each testcase using steps
def process_steps(test_steps, testbed, steps, params):
    for step in test_steps:
        with steps.start(step['desc']):
            if testbed.devices[step['device']].connected or step['device'] == 'dummy':
                if 'action_chain' in step.keys():
                    for seq in range(len(step['action_chain'])):
                        func = globals()[step['action_chain'][seq]['action']] 
                        func(testbed, step['device'], step['action_chain'][seq]['action_vars'], params)
            else:
                aetest.steps.Step.failed('Device was not connected')
                
#testcase classes which will take data from datafile
class Testcase_C1(aetest.Testcase):
    
    @aetest.setup
    def setup(self, testbed, steps, params):
        if self.setup_steps is not None:
            process_steps(test_steps = self.setup_steps, testbed = testbed, steps=steps, params=params)
        if self.tests is not None:
            aetest.loop.mark(self.test, uids=list(self.tests))
        else:
            aetest.skip('No tests specified')

    @aetest.test
    def test(self, testbed, steps, section, params):
        if self.tests is not None:
            process_steps(test_steps = self.tests[section.uid], testbed = testbed, steps=steps, params=params)
        else:
            aetest.skip('No tests specified')

    @aetest.cleanup
    def cleanup(self, testbed, steps, params):
        if self.cleanup_steps is not None:
            process_steps(test_steps = self.cleanup_steps, testbed = testbed, steps=steps, params=params)

class Testcase_C2(Testcase_C1):
    pass

class Testcase_C3(Testcase_C1):
    pass

class Testcase_C4(Testcase_C1):
    pass

class Testcase_C5(Testcase_C1):
    pass

class Testcase_C6(Testcase_C1):
    pass

# main()
if __name__ == '__main__':

    # set logger level
    logger.setLevel(logging.INFO)

    # local imports
    import sys
    import argparse
    from pyats.topology import loader

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--params', dest = 'params')

    # parse args
    args, sys.argv[1:] = parser.parse_known_args(sys.argv[1:])

    # post-parsing processing    
    params = args.params

    # and pass all arguments to aetest.main() as kwargs
    aetest.main(params = params)