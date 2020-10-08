# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceFM(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('', service._path, ': Processing cb_create')

        vars = ncs.template.Variables()

        self.log.info('', service._path, ': Applying template v1')
        template = ncs.template.Template(service)
        template.apply('template-version1', vars)

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
