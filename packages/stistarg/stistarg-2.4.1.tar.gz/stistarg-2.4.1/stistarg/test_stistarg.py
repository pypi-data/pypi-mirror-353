import stistarg

import numpy as np
from astropy.io import fits
import os
import sys
from unittest.mock import patch
import warnings
import glob
import tempfile
import unittest
warnings.filterwarnings('ignore',
    message='matplotlib is currently using a non-GUI backend, so cannot show the figure',
    module='matplotlib')
import matplotlib
matplotlib.use('Agg')  # prevents plotting to a window
from matplotlib import pyplot as plt


# ----------------------------------------------------------------------------------------
# Helper functions:

assertions = unittest.TestCase('__init__')
assert_almost_equals = assertions.assertAlmostEqual
assert_equals = assertions.assertAlmostEqual


def gaussarr(x, y, xsize=200, ysize=200, fwhm=10, height=300):
    '''
    Example function that generates an array with a Gaussian.
    '''
    from astropy.modeling.models import Gaussian2D

    arr = np.zeros((xsize, ysize))
    std = fwhm / (2. * np.sqrt(2. * np.log(2.)))
    g = Gaussian2D(x_mean=x, y_mean=y, x_stddev=std, y_stddev=std)
    g.render(arr)
    outarr = np.asarray(np.around(arr * height), dtype=np.int32)
    outarr += 1
    return outarr


def write_slope():
    z = np.zeros((200, 200))
    for i in range(200):
        z[i, :] += i
    return z


# ----------------------------------------------------------------------------------------
# Unit Tests:

class TestCheckbox(object):
    @classmethod
    def setup_class(cls):
        '''This method is run once for each class before any tests are run.'''
        # Create a temporary directory:
        cls.tmpdir = tempfile.mkdtemp(prefix='tmp_stistarg_')

    @classmethod
    def teardown_class(cls):
        '''This method is run once for each class after all tests are run.'''
        # Remove temporary directory and all files contained therein:
        files = glob.glob(os.path.join(cls.tmpdir, '*'))
        for f in files:
            os.remove(f)
        os.rmdir(cls.tmpdir)

    def test1(self):
        filename = os.path.join(self.tmpdir, 'test1.fits')
        arr = gaussarr(15, 30, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3, display=False)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 16. - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 31. - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 877, places=5)
        assert_equals(stistarg_results['checkbox_x'], 14)
        assert_equals(stistarg_results['checkbox_y'], 29)

    def test2(self):
        filename = os.path.join(self.tmpdir, 'test2.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 31 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 16 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 877, places=5)

    def test3(self):
        filename = os.path.join(self.tmpdir, 'test3.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100) + gaussarr(40, 25, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 31.002251 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 16.002251 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 889, places=5)

    def test4(self):
        filename = os.path.join(self.tmpdir, 'test4.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100) + gaussarr(40, 25, fwhm=10, height=200)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 40.998863 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 25.998861 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 1757, places=5)

    def test5(self):
        filename = os.path.join(self.tmpdir, 'test5.fits')
        arr = gaussarr(15, 30, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=25)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 16 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 31 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 11861, places=5)
        assert_equals(stistarg_results['checkbox_x'], 3)
        assert_equals(stistarg_results['checkbox_y'], 18)

    def test6(self):
        filename = os.path.join(self.tmpdir, 'test6.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=25)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 31 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 16 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 11861, places=5)

    def test7(self):
        filename = os.path.join(self.tmpdir, 'test7.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100) + gaussarr(40, 25, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=25)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 36 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 21 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 22158, places=5)

    def test8(self):
        filename = os.path.join(self.tmpdir, 'test8.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100) + gaussarr(40, 25, fwhm=10, height=200)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=25)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 37.835854 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 22.835852 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 32824, places=5)

    def test12(self):
        filename = os.path.join(self.tmpdir, 'test12.fits')
        arr = gaussarr(60, 80, fwhm=10, height=200) + gaussarr(39.5, 54.5, fwhm=10, height=201)+write_slope()
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 61.000000 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 81.002426 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 2474, places=5)

    def test13(self):
        filename = os.path.join(self.tmpdir, 'test13.fits')
        arr = gaussarr(60, 80, fwhm=10, height=300) + gaussarr(39.5, 54.5, fwhm=10, height=201)+write_slope()
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='point', checkboxsize=3)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 61.000000 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 81.001793 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 3342, places=5)

    def test14(self):
        filename = os.path.join(self.tmpdir, 'test14.fits')
        arr = gaussarr(60, 75, fwhm=30, height=75) + gaussarr(40, 50, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=33)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 60.986961 - 1., places=5)
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 75.986252 - 1., places=5)
        assert_almost_equals(stistarg_results['checkboxFlux'], 51776, places=5)

    def test_original(self):
        filename = os.path.join(self.tmpdir, 'test_original.fits')
        arr = gaussarr(30, 15, fwhm=10, height=100) + gaussarr(40, 25, fwhm=10, height=200)
        fits.writeto(filename, arr, overwrite=True)
        stistarg_results = stistarg.stistarg(filename, source='diffuse', checkboxsize=25)
        assert_almost_equals(stistarg_results['fluxCentroid'][0], 37.835854 - 1., places=5)  # Results from Solaris binary
        assert_almost_equals(stistarg_results['fluxCentroid'][1], 22.835852 - 1., places=5)  # Results from Solaris binary

    def test_display(self, monkeypatch):
        monkeypatch.setattr(plt.Figure, 'show', lambda x: None)
        monkeypatch.setattr("builtins.input", lambda x: None)

        filename = os.path.join(self.tmpdir, 'test_display.fits')
        arr = gaussarr(15, 30, fwhm=10, height=100)
        fits.writeto(filename, arr, overwrite=True)
        _ = stistarg.stistarg(filename, source='diffuse', checkboxsize=5, display=True)


def test_parse_point(monkeypatch):
    test_args = ["stistarg", "test.fits"]
    monkeypatch.setattr(sys, "argv", test_args)

    with patch("stistarg.main.stistarg") as mock_stistarg:
        stistarg.parse()
        mock_stistarg.assert_called_once_with("test.fits", 0, "point", 3, False)


def test_parse_diffuse(monkeypatch):
    test_args = ["stistarg", "test.fits", "--diffuse", "7"]
    monkeypatch.setattr(sys, "argv", test_args)

    with patch("stistarg.main.stistarg") as mock_stistarg:
        stistarg.parse()
        mock_stistarg.assert_called_once_with("test.fits", 0, "diffuse", 7, False)
