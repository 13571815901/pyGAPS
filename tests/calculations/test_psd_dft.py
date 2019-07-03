"""
This test module has tests relating to DFT fitting for pore size calculations.

All functions in /calculations/psd_dft.py are tested here.
The purposes are:

    - testing the user-facing API function (psd_dft)
    - testing individual low level functions against known results.

Functions are tested against pre-calculated values on real isotherms.
It is difficult to store full pore size distributions, therefore the
cumulative pore volume as determined by each method is checked
versus stored values.
All pre-calculated data for characterization can be found in the
/.conftest file together with the other isotherm parameters.
"""

import os

import pytest
from matplotlib.testing.decorators import cleanup
from numpy import isclose

import pygaps
import pygaps.calculations.psd_dft as pdft
from pygaps.utilities.exceptions import ParameterError

from .conftest import DATA
from .conftest import DATA_N77_PATH


@pytest.mark.characterisation
class TestPSDDFT():
    """Test pore size distribution calculation."""

    def test_psd_dft_checks(self, basic_pointisotherm):
        """Checks for built-in safeguards."""
        # Will raise a "no kernel exception"
        with pytest.raises(ParameterError):
            pdft.psd_dft(basic_pointisotherm, kernel=None)

        # Will raise a "no applicable branch exception"
        with pytest.raises(ParameterError):
            pdft.psd_dft(basic_pointisotherm, branch='test')

    @pytest.mark.parametrize('kernel', [
        'DFT-N2-77K-carbon-slit',
    ])
    @pytest.mark.parametrize('sample', [
        sample for sample in list(DATA.values())
    ])
    def test_psd_dft(self, sample, kernel):
        """Test psd calculation with several model isotherms"""
        # exclude datasets where it is not applicable
        if sample.get('psd_dft_pore_volume', None):

            filepath = os.path.join(DATA_N77_PATH, sample['file'])

            with open(filepath, 'r') as text_file:
                isotherm = pygaps.isotherm_from_json(text_file.read())

            result_dict = pdft.psd_dft(isotherm, kernel=kernel)

            err_relative = 0.1  # 10 percent
            err_absolute = 0.01  # 0.01 cm3/g

            assert isclose(
                result_dict['pore_volume_cumulative'][-1],
                sample['psd_dft_pore_volume'],
                err_relative, err_absolute)

    @cleanup
    def test_psd_dft_verbose(self):
        """Test verbosity."""
        data = DATA['MCM-41']
        filepath = os.path.join(DATA_N77_PATH, data['file'])

        with open(filepath, 'r') as text_file:
            isotherm = pygaps.isotherm_from_json(
                text_file.read())

        pygaps.psd_dft(isotherm, verbose=True)
