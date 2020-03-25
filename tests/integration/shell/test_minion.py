# -*- coding: utf-8 -*-
'''
    :codeauthor: Pedro Algarvio (pedro@algarvio.me)


    tests.integration.shell.minion
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Import python libs
from __future__ import absolute_import
import time
import logging

import salt.defaults.exitcodes
from saltfactories.utils.processes.salts import SaltMinion

import pytest

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def shell_tests_salt_master(request, salt_factories):
    return salt_factories.spawn_master(request, 'shell-tests-master')


@pytest.fixture(scope='module')
def shell_tests_salt_minion_config(request, salt_factories, shell_tests_salt_master):
    return salt_factories.configure_minion(request,
                                           'shell-tests-minion',
                                           master_id=shell_tests_salt_master.config['id'],
                                           config_overrides={'user': 'unknown-user'})


@pytest.mark.windows_whitelisted
class TestSaltMinionCLI(object):
    def test_exit_status_unknown_user(self, salt_minion, shell_tests_salt_minion_config):
        '''
        Ensure correct exit status when the minion is configured to run as an unknown user.
        '''
        proc = SaltMinion(
            cli_script_name=salt_minion.cli_script_name,
            config=shell_tests_salt_minion_config
        )
        proc.start()
        iterations = 20
        while proc.is_alive():
            if not iterations:
                break
            time.sleep(1)
            iterations -= 1
        ret = proc.terminate()
        assert ret.exitcode == salt.defaults.exitcodes.EX_NOUSER
        assert 'The user is not available.' in ret.stderr

    def test_exit_status_unknown_argument(self, salt_minion, shell_tests_salt_minion_config):
        '''
        Ensure correct exit status when an unknown argument is passed to salt-minion.
        '''
        proc = SaltMinion(
            cli_script_name=salt_minion.cli_script_name,
            config=shell_tests_salt_minion_config,
            base_script_args=['--unknown-argument']
        )
        proc.start()
        iterations = 20
        while proc.is_alive():
            if not iterations:
                break
            time.sleep(1)
            iterations -= 1
        ret = proc.terminate()
        assert ret.exitcode == salt.defaults.exitcodes.EX_USAGE, ret
        assert 'Usage' in ret.stderr
        assert 'no such option: --unknown-argument' in ret.stderr

    def test_exit_status_correct_usage(self, request, salt_factories, shell_tests_salt_master):
        proc = salt_factories.spawn_minion(request,
                                           'shell-tests-minion-2',
                                           master_id=shell_tests_salt_master.config['id'])
        assert proc.is_alive()
        time.sleep(1)
        ret = proc.terminate()
        assert ret.exitcode == salt.defaults.exitcodes.EX_OK, ret
