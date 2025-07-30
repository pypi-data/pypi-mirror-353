#!/usr/bin/env python
import importlib.resources
import os
import tempfile
import zipfile
import subprocess


import pycrtomo


def check_pycrtomo_as_module():
    inv_zip_file = str(
        str(importlib.resources.files('crtomo_tests')) +
        os.sep +
        'data' +
        os.sep +
        'example_inversion_01.zip'
    )
    with tempfile.TemporaryDirectory() as tempdir:
        print('tempdir', tempdir)
        zipobj = zipfile.ZipFile(inv_zip_file)
        zipobj.extractall(tempdir)
        basedir = tempdir + os.sep + 'example_inversion_01' + os.sep
        pwd = os.getcwd()
        os.chdir(basedir + 'exe')
        r = pycrtomo.pyinv.invertpy()
        print('Return value', r)
        # now check
        assert os.path.isfile(basedir + os.sep + 'inv' + os.sep + 'inv.ctr'), \
            'inv.ctr was not created'

        os.chdir(pwd)
        print('Press enter to continue')
        input()


def check_pycrtomo_as_script():
    inv_zip_file = str(
        str(importlib.resources.files('crtomo_tests')) +
        os.sep +
        'data' +
        os.sep +
        'example_inversion_01.zip'
    )
    with tempfile.TemporaryDirectory() as tempdir:
        print('tempdir', tempdir)
        zipobj = zipfile.ZipFile(inv_zip_file)
        zipobj.extractall(tempdir)
        basedir = tempdir + os.sep + 'example_inversion_01' + os.sep
        pwd = os.getcwd()
        os.chdir(basedir + 'exe')
        try:
            subprocess.check_output('CRTomo', shell=True)
        except subprocess.CalledProcessError as error:
            print('There was an error calling CRTomo')
            print(error.output)
            print('Return code: {}'.format(error.returncode))
            os.chdir(pwd)
            raise Exception('Error calling the CRTomo script')
        os.chdir(pwd)


def main():
    check_pycrtomo_as_module()
    check_pycrtomo_as_script()
