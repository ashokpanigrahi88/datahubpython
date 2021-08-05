from setuptools import setup

setup(
    name='oratech',
    version='1.0',
    packages=['sales', 'sales.migrations', 'setup', 'setup.forms', 'setup.views', 'setup.migrations', 'common',
              'common.migrations', 'common.templatetags', 'mobile', 'mobile.views', 'mobile.migrations', 'oratech',
              'restapi', 'restapi.migrations', 'purchase', 'purchase.migrations', 'inventory', 'inventory.migrations',
              'warehouse', 'warehouse.migrations'],
    url='http://www.oratechsolutions.biz',
    license='oratech',
    author='Administrator',
    author_email='admin@oratechsolutions.biz',
    description='Oratech  Warehouse Management System'
)
