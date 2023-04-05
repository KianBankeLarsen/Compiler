from __future__ import annotations

import argparse
import copy
import io
import os
import subprocess
import unittest
from collections import defaultdict
from contextlib import redirect_stderr

import src.compiler


class TestCase(unittest.TestCase):
    """
    """

    def __init__(self, methodName: str, res: str, src: str, args: argparse.Namespace) -> TestCase:
        super().__init__(methodName)

        self.res = res
        self.src = src

        self.args = args

        self._testMethodDoc = f"Testing {self.src}"

    def _files_equal(self, file1, file2):
        with open(file1, 'r') as f:
            file1_content = f.readlines()

        with open(file2, 'r') as f:
            file2_content = f.readlines()

        return file1_content == file2_content

    def runTest(self):
        """
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
                os.remove(f"{self.src}.iloc")


def load_tests(args: argparse.Namespace) -> unittest.TestSuite:
    """
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
        test_cases.addTest(TestCase('runTest', res, src, args))

    return test_cases
