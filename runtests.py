#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django_version = '.'.join([str(seg) for seg in django.VERSION])
    if django_version.startswith('1.7'):
        django.setup()
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
