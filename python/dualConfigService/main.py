# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceFM(Service):

    @Service.pre_modification
    def cb_pre_modification(self, tctx, op, kp, root, proplist):
        self.log.info('', kp, ': Is this a new service (0 - create, 1 - modify, 2 - delete): ', op)
        if op == ncs.dp.NCS_SERVICE_CREATE:
            proplist.append(('newServiceInstance', 'True'))
        return proplist

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('', service._path, ': Processing cb_create')
        dualConfigVars = {'newServiceInstance': "False"}

        try:
            dualConfigVars['newServiceInstance'] = [x[1] for x in proplist if x[0] == 'newServiceInstance'][0]
            self.log.info('', service._path, ': Instance created after pkg upgrade')
        except IndexError as e:
            #for existing instances, this structure does not exist
            self.log.info('', service._path, ': Instance existed before pkg upgrade')
            pass

        vars = ncs.template.Variables()

        if dualConfigVars['newServiceInstance'] == 'True':
            self.log.info('', service._path, ': Applying template v2 - new service instance, use new version')
            service.configurationVersion.value = 2
            template = ncs.template.Template(service)
            template.apply('template-version2', vars)
            for dev in service.device:
                for entry in dev.blacklist_custom:
                    varsC = ncs.template.Variables()
                    varsC.add('DEVICENAME', dev.name)
                    varsC.add('DCS_NAME', service.name)
                    varsC.add('IPADDRESS', entry.ip_address)
                    template.apply('template-version2-custom', varsC)
        elif service.configurationVersion.value == 1:
            self.log.info('', service._path, ': Applying template v1')
            template = ncs.template.Template(service)
            template.apply('template-version1', vars)
        elif service.configurationVersion.value == 2:
            self.log.info('', service._path, ': Applying template v2 - new service instance, use new version')
            service.configurationVersion.value = 2
            template = ncs.template.Template(service)
            template.apply('template-version2', vars)
            for dev in service.device:
                for entry in dev.blacklist_custom:
                    varsC = ncs.template.Variables()
                    varsC.add('DEVICENAME', dev.name)
                    varsC.add('DCS_NAME', service.name)
                    varsC.add('IPADDRESS', entry.ip_address)
                    template.apply('template-version2-custom', varsC)
        else:
            raise NotImplementedError("Version is not supported. Please verify settings.")
        
        self.log.info('', service._path, ': Exiting.')

    

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('dualConfigService-svcpoint', ServiceFM)

    def teardown(self):
        self.log.info('Main FINISHED')
