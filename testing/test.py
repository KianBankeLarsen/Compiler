from __future__ import annotations

import argparse
import copy
import os
import unittest
from collections import defaultdict

import src.compiler


class TestCase(unittest.TestCase):
    """
    """

    def __init__(self, methodName: str, res: str, src: str, args: argparse.Namespace) -> TestCase:
        super(TestCase, self).__init__(methodName)

        self.res = res
        self.src = src

        self.args = args

        self._testMethodDoc = f"Running test for {self.src}"

    def runTest(self):
        src.compiler.PandaCompiler(self.args).compile()
        os.remove(f"{self.src}.s")
        os.remove(f"{self.src}.out")


def load_tests(args: argparse.Namespace) -> unittest.TestSuite:
    """
    """

    args = copy.copy(args)
    args.compile = True

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
