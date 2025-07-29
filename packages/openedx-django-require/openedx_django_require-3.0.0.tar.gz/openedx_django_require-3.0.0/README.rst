openedx-django-require
######################

|pypi-badge| |ci-badge| |codecov-badge|

.. |pypi-badge| image:: https://img.shields.io/pypi/v/openedx-django-require.svg
    :target: https://pypi.python.org/project/openedx-django-require/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/django-require/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/openedx/django-require/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/django-require/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/django-require?branch=main
    :alt: Codecov


**django-require** is a Django staticfiles post-processor for optimizing
with `RequireJS <http://requirejs.org/>`_.

*In the context of the Open edX project*, this django-require fork is used exclusively by
legacy frontend code in `edx-platform <https://github.com/openedx/edx-platform>`_.
That frontend code is all either replaced or in the process of being replaced.
Once this process is complete, edx-platform will no longer need to
install django-require, and this fork will be archived. As such, please
consider this repository effectively deprecated and **do not use it in any
new code**.

License
*******

This software:

* was forked from https://github.com/edx/django-require,
* which was forked from https://github.com/vtemian/django-require,
* which was forked from https://github.com/etianen/django-require.

All contribution made to those repositories, the last of which
is tagged `final-bsd-3c-contribution`_, are licensed by the original
contributors under the terms of the `BSD 3-Clause License`_.

The software is now maintained for the purpose of the Open edX
project by Axim Collaborative, Inc., which licenses
any further contributions to this repository under the `Apache License 2.0`_.

.. _final-bsd-3c-contribution: https://github.com/openedx/django-require/releases/tag/final-bsd-3c-contribution
.. _Apache License 2.0: ./LICENSE
.. _BSD 3-Clause License: ./LICENSE-BSD-3c

Contributing
************

Bugfixes and routine maintenance contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.
Thank you!

This repository is not accepting any new features nor refactors.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/django-require

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

django-require (Original Documentation)
#######################################

Features
********

-  Optimize your static assets using the excellent r.js optimizer.
-  Compile standalone modules using the
   `almond.js <https://github.com/requirejs/almond>`_ shim.
-  Compatible with any Django staticfiles storage backend.

Installation
************

1. Checkout the latest django-require release and copy or symlink the
   ``require`` directory into your ``PYTHONPATH``.  If using pip, run
   ``pip install django-require``.
2. Add ``'require'`` to your ``INSTALLED_APPS`` setting.
3. Set your ``STATICFILES_STORAGE`` setting to
   ``'require.storage.OptimizedStaticFilesStorage'``,
   ``'require.storage.OptimizedCachedStaticFilesStorage'`` or
   ``'require.storage.OptimizedManifestStaticFilesStorage'``.

Available settings
******************

Available settings, and their default values, are shown below. You
should configure this to match the layout of your project's static
files. Please consult the `RequireJS <http://requirejs.org/>`_
documentation for more information about how to build javascript using
RequireJS.

.. code:: python

    # The baseUrl to pass to the r.js optimizer, relative to STATIC_ROOT.
    REQUIRE_BASE_URL = "js"

    # The name of a build profile to use for your project, relative to REQUIRE_BASE_URL.
    # A sensible value would be 'app.build.js'. Leave blank to use the built-in default build profile.
    # Set to False to disable running the default profile (e.g. if only using it to build Standalone
    # Modules)
    REQUIRE_BUILD_PROFILE = None

    # The name of the require.js script used by your project, relative to REQUIRE_BASE_URL.
    REQUIRE_JS = "require.js"

    # A dictionary of standalone modules to build with almond.js.
    # See the section on Standalone Modules, below.
    REQUIRE_STANDALONE_MODULES = {}

    # Whether to run django-require in debug mode.
    REQUIRE_DEBUG = settings.DEBUG

    # A tuple of files to exclude from the compilation result of r.js.
    REQUIRE_EXCLUDE = ("build.txt",)

    # The execution environment in which to run r.js: auto, node or rhino.
    # auto will auto-detect the environment and make use of node if available and rhino if not.
    # It can also be a path to a custom class that subclasses
    # require.environments.Environment and defines some "args" function that
    # returns a list with the command arguments to execute.
    REQUIRE_ENVIRONMENT = "auto"

Generating require.js
*********************

As a shortcut to downloading a copy of require.js from the internet, you
can simply run the ``require_init`` management to copy a version of
require.js into your ``STATICFILES_DIRS``, at the location specified by
your ``REQUIRE_BASE_URL`` and ``REQUIRE_JS`` settings.

.. code:: bash

    $ ./manage.py require_init

Generating build profiles
*************************

In almost all cases, you'll want to create a custom build profile for
your project. To help you get started, django-require can generate a
default build profile into your ``STATICFILES_DIRS``. Just set your
``REQUIRE_BUILD_PROFILE`` setting to a build profile name, and run
``require_init``. A good name for a build profile would be
``'app.build.js'``.

Any standalone modules that your specify with a build profile will also
have a default build profile generated when you run this command.

Running javascript modules in templates
***************************************

You can run javascript modules in templates by using the
``{% require_module %}`` template tag.

.. code:: html

    <html>
        {% load require %}
        <head>
            {% require_module 'main' %}
        </head>
        <body></body>
    </html>

This template fragment would then render to something like:

.. code:: html

    <html>
        <head>
            <script src="/static/js/require.js" data-main="/static/js/main.js"></script>
        </head>
        <body></body>
    </html>

If the ``'main'`` module was specified as a standalone module in your
``REQUIRE_STANDALONE_MODULES`` setting, and ``REQUIRE_DEBUG`` is
``False``, then the template fragment would instead render as:

This template fragment would then render to something like:

.. code:: html

    <html>
        <head>
            <script src="/static/js/main-built.js"></script>
        </head>
        <body></body>
    </html>

Building standalone modules
***************************

As a further optimization to your code, you can build your modules to
run independently of require.js, which can often speed up page load
times. Standalone modules are built using the almond.js shim, so consult
the `almond.js <https://github.com/requirejs/almond>`_ documentation to
make sure that it's safe to build your module in standalone mode.

To specify standalone modules, simply add them to your
``REQUIRE_STANDALONE_MODULES`` setting, as below:

.. code:: python

    REQUIRE_STANDALONE_MODULES = {
        "main": {
            # Where to output the built module, relative to REQUIRE_BASE_URL.
            "out": "main-built.js",

            # Optional: A build profile used to build this standalone module.
            "build_profile": "main.build.js",
        }
    }

Running the r.js optimizer
**************************

The r.js optimizer is run automatically whenever you call the
``collectstatic`` management command. The optimizer is run as a
post-processing step on your static files.

django-require provides three storage classes that are ready to use with
the r.js optimizer:

-  ``require.storage.OptimizedStaticFilesStorage`` - A filesystem-based
   storage that runs the r.js optimizer.
-  ``require.storage.OptimizedCachedStaticFilesStorage`` - As above, but
   fingerprints all files with an MD5 hash of their contents for HTTP
   cache-busting.
-  ``require.storage.OptimizedManifestStaticFilesStorage`` - As above, but
   fingerprints all files with an MD5 hash of their contents for HTTP
   cache-busting and stores the fingerprints in a JSON file on disk instead
   of using a cache. Please note that the
   ``OptimizedManifestStaticFilesStorage`` is only available in Django 1.7 and
   above.

Creating your own optimizing storage classes
********************************************

You can add r.js optimization to any Django staticfiles storage class by
using the ``require.storage.OptimizedFilesMixin``. For example, to make
an optimizing storage that uploads to Amazon S3 using ``S3BotoStorage``
from
`django-storages <http://django-storages.readthedocs.org/en/latest/>`_:

.. code:: python

    from storages.backends.s3boto import S3BotoStorage
    from require.storage import OptimizedFilesMixin

    # S3 storage with r.js optimization.
    class OptimizedS3BotoStorage(OptimizedFilesMixin, S3BotoStorage):
        pass

    # S3 storage with r.js optimization and MD5 fingerprinting.
    from django.contrib.staticfiles.storage import CachedFilesMixin
    class OptimizedCachedS3BotoStorage(OptimizedFilesMixin, CachedFilesMixin, S3BotoStorage):
        pass

For ready-made storage classes that combine django-require with Amazon S3, check out
`django-require-s3 <https://github.com/etianen/django-require-s3>`_.

Other projects extending django-require
***************************************

- `django-require-license <https://github.com/collab-project/django-require-license>`_ - prepends a license header to compressed file(s) generated with django-require

Tests
*****

You can run the test suite from the root of the source checkout::

    test_project/manage.py test require

Test coverage reports can be generated from the same directory with::

    coverage run --source='.' test_project/manage.py test require
    coverage html

Open `htmlcov/index.html` in a browser to see the HTML coverage report.

Support and announcements
*************************

Downloads and bug tracking can be found at the `main project
website <http://github.com/etianen/django-require>`_.

You can keep up to date with the latest announcements by joining the
`django-require discussion
group <http://groups.google.com/group/django-require>`_.

More information
****************

The django-require project was developed by Dave Hall. You can get the
code from the `django-require project
site <http://github.com/etianen/django-require>`_.

Dave Hall is a freelance web developer, based in Cambridge, UK. You can
usually find him on the Internet in a number of different places:

-  `Website <http://www.etianen.com/>`_
-  `Twitter <http://twitter.com/etianen>`_
-  `Google Profile <http://www.google.com/profiles/david.etianen>`_
