#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    # Run Main Tests
    from django.test.utils import get_runner
    # Run post-processor tests
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.post_processor.test_settings'
    if django.VERSION >= (1, 7):
        django.setup()
    TestRunnerPostProcessor = get_runner(
        settings,
        'tests.post_processor.discover_tests.DiscoverPostProcessorRunner'
    )
    test_runner_post_processor = TestRunnerPostProcessor()
    failures = test_runner_post_processor.run_tests(["tests.post_processor"])
    sys.exit(bool(failures))
