from __future__ import annotations

import argparse
import copy
import io
import os
import shutil
import subprocess
import unittest
from collections import defaultdict
from contextlib import redirect_stderr

import src.compiler


class TestCase(unittest.TestCase):
    """Default subclass of unittest.TestCase.
    """

    def __init__(self, res: str, src: str, args: argparse.Namespace) -> TestCase:
        super().__init__()

        self.res = res
        self.src = src

        self.args = args

        self._testMethodDoc = f"Testing {self.src}"

    def _files_equal(self, file1, file2):
        """Compares whether files share identical content.
        """
        
        with open(file1, 'r') as f:
            file1_content = f.readlines()

        with open(file2, 'r') as f:
            file2_content = f.readlines()

        return file1_content == file2_content

    def runTest(self):
        """Controls how the unittest should proceed.
        """
        
        output = f"{self.src}.out.tmp"

        exit_code = None

        with io.StringIO() as buf, redirect_stderr(buf):
            try:
                src.compiler.PandaCompiler(self.args).compile()
            except SystemExit:
                exit_code = True
                with open(output, "w") as f:
                    f.write(buf.getvalue())

        if exit_code:
            assert self._files_equal(self.res, output)
            os.remove(output)
        else:
            with open(output, "w") as f:
                subprocess.call([f"./{self.src}.out"], stdout=f)

            assert self._files_equal(self.res, output)

            os.remove(f"{self.src}.s")
            os.remove(f"{self.src}.out")
            os.remove(output)

            if self.args.debug:
                os.remove(f"{self.src}.stack.iloc")

                file_name = os.path.basename(self.src)
                os.remove(f"src/printer/images/AST.testing/test-cases/{file_name}.gv.png")
                os.remove(f"src/printer/images/AST.testing/test-cases/{file_name}.gv")
                os.remove(f"src/printer/images/AST-desugar.testing/test-cases/{file_name}.gv.png")
                os.remove(f"src/printer/images/AST-desugar.testing/test-cases/{file_name}.gv")
                os.remove(f"src/printer/images/Symbol.testing/test-cases/{file_name}.gv.png")
                os.remove(f"src/printer/images/Symbol.testing/test-cases/{file_name}.gv")


def load_tests(args: argparse.Namespace) -> unittest.TestSuite:
    """Dynamically create a test suite, containing a test for every 
    test-pair specified in the ```testing/test-cases``` folder.
    """

    args = copy.copy(args)
    args.compile = True
    args.run = False

    file_dict = defaultdict(list)
    test_cases = unittest.TestSuite()

    for dir_path, _, file_names in os.walk("testing/test-cases"):
        for file_name in file_names:
            file = f"{dir_path}/{file_name}"
            name, ext = os.path.splitext(file)

            if ext not in [".panda", ".eop"]:
                continue

            if ext == ".eop":
                file_dict[name].insert(0, file)
            else:
                file_dict[name].append(file)

    for res, src in file_dict.values():
        args = copy.copy(args)
        args.output = src
        args.file = src
        test_cases.addTest(TestCase(res, src, args))

    return test_cases
