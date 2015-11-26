'''
Base configuration file for sphinx-build.

You can override this configuration by putting 'conf.py' in the document
directory (e.g. how-to-use-docs/conf.py). If there is no 'conf.py' in the
document directory, this file will be copied to that directory before the
document builder jobs in 'opnfv-docs-verify' and 'opnfv-docs-merge'.
The logo image (opnfv-logo.png) will be also copied from
docs/etc/opnfv-logo.png during the build jobs.
'''

import datetime

needs_sphinx = '1.3'
master_doc = 'index'
pygments_style = 'sphinx'

html_use_index = False
numfig = True
html_logo = 'opnfv-logo.png'

latex_elements = {'printindex': ''}
latex_logo = 'opnfv-logo.png'

copyright = u'%s, OPNFV' % datetime.date.today().year
version = u'1.0.0'
release = u'1.0.0'
