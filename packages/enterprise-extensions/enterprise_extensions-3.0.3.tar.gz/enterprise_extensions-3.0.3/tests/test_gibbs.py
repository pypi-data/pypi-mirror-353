# -*- coding: utf-8 -*-

"""
Tests for the gibbs sampling code.
"""

import logging
import os
from enterprise.pulsar import FeatherPulsar
from enterprise_extensions.gibbs_sampling import gibbs
import pytest

testdir = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(testdir, 'data')


psr_names = ['J0613-0200']


@pytest.fixture
def nodmx_psrs(caplog):
    caplog.set_level(logging.CRITICAL)
    psrs = []
    for p in psr_names:
        psrs.append(FeatherPulsar.read_feather(datadir+'/{0}_ng11yr_nodmx_DE436_epsr.feather'.format(p)))

    return psrs


def test_gibbs(nodmx_psrs, caplog):

    psr = nodmx_psrs[0]
    BPC = gibbs.BayesPowerSingle(
        psr=psr,
        Tspan=None,
        select='backend',
        white_vary=True,
        inc_ecorr=True,
        ecorr_type='kernel',
        noise_dict=None,
        tm_marg=False,
        freq_bins=10,
        log10rhomin=-9.,
        log10rhomax=-4.)

    assert hasattr(BPC, 'sample')
