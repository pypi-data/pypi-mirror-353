"""
Copyright 1999 Illinois Institute of Technology

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL ILLINOIS INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name of Illinois Institute
of Technology shall not be used in advertising or otherwise to promote
the sale, use or other dealings in this Software without prior written
authorization from Illinois Institute of Technology.
"""

python_version = { "python" : "3.10.6" }
pip_details = {
    "scikit-image" : "0.19.3",
    "tifffile" : "2023.1.23",
    "numpy" : "1.23.5",
    "pandas" : "1.5.3",
    "scikit-learn" : "1.2.0",
    "lmfit" : "1.1.0",
    "fabio" : "2022.12.1",
    "h5py" : "3.8.0",
    "scipy" : "1.10.0",
    "matplotlib" : "3.6.3",
    "opencv-python-headless" : "4.7.0",
    "pyFAI" : "2023.1.0",
    "distro" : "1.8.0",
    "hdf5plugin" : "4.1.1",
    "PyMca5" : "5.8.0",
    "numba" : "0.56.4",
    "fisx" : "1.2.0",
    "future" : "0.18.2",
    "openpyxl" : "3.1.1",
    "pip" : "23.2.1",
    "wheel" : "0.37.1"
    }

import os
import sys
import unittest
from time import gmtime, strftime
import platform
from musclex import __version__

class EnvironmentTester(unittest.TestCase):
    """
    Unittest class to test the pip environment of the computer, UPDATE BEFORE RELEASE
    """
    @classmethod
    def setUpClass(cls):
        if getattr(sys, 'frozen', False):
            cls.currdir = os.path.join(os.path.dirname(sys._MEIPASS), "musclex")
        else:
            cls.currdir = os.path.dirname(__file__)
        cls.inpath = os.path.join(cls.currdir, "test_images")
        cls.testversion = __version__ # change this to test against a different version

        cls.logname = os.path.join(cls.currdir,"test_logs", "test.log")
        if not os.path.isdir(os.path.dirname(cls.logname)):
            os.mkdir(os.path.dirname(cls.logname))
        if os.path.exists(cls.logname):
            append_write = 'a'
        else:
            append_write = 'w'

        with open(cls.logname, append_write) as lf:
            lf.write(f'\n{"-"*80}\n')
            lf.write("Beginning test at {}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
            lf.write("Testing MuscleX version: {}\n".format(__version__))
            lf.write("\nSummary of Test Results\n")

    @classmethod
    def tearDownClass(cls):
        with open(cls.logname, 'a') as lf:
            lf.write("Ending test at {}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
            lf.write(f'\n{"-"*80}\n')

    def testEnvironment(self):
        """
        Runs a test of Environment given the current versions.
        """
        print(f"\033[3;33m\nVerifying that installed Python version {python_version['python']} is equivalent to Python at the release {__version__}\033[0;3140m")
        if platform.python_version() == python_version["python"]:
            print("Testing Python version ..... \033[0;32mPASSED\033[0;3140m")
            python_test = True
        else:
            print(f"Testing Python version ..... \033[0;31mWARNING : {platform.python_version()} is not {python_version['python']}\033[0;3140m")
            python_test = False
        self.log_results(python_test, "Python Version")
        for pip in pip_details:
            pass_test = env_test(pip, pip_details)
            self.log_results(pass_test, pip)
        # self.assertTrue(pass_test,"Environment Test failed.")

    def log_results(self, pass_test, testname):
        """
        Save the result in the log file
        """
        if pass_test:
            result = 'pass'
        else:
            result = 'warning, check terminal for more detail'
        with open(self.logname, 'a') as lf:
            lf.write(f"{testname} Test: {result}\n")

def env_test(pip, pip_details):
    """
    Function importing the package pip and comparing the version to the package version at the release
    """
    print(f"\033[3;33m\nVerifying that installed package {pip} is equivalent to package at the release {__version__}\033[0;3140m")
    if pip == "scikit-image":
        module = __import__("skimage")
    elif pip == "scikit-learn":
        module = __import__("sklearn")
    elif pip == "opencv-python-headless":
        module = __import__("cv2")
    else:
        module = __import__(pip)
    if pip in ("fabio", "pyFAI", "hdf5plugin"):
        vfy_pip = module.version
    else:
        vfy_pip = module.__version__
    pass_test = (vfy_pip == pip_details[pip])
    if pass_test:
        print(f"Testing {pip} ..... \033[0;32mPASSED\033[0;3140m")
    else:
        print(f"Testing {pip} ..... \033[0;31mWARNING : {vfy_pip} is not {pip_details[pip]}\033[0;3140m")
    return pass_test

if __name__=="__main__":
    unittest.main(verbosity=2)
