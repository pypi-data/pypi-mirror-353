# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import benchexec.result as result
import benchexec.tools.template
from math import ceil


class Tool(benchexec.tools.template.BaseTool2):
    """
    Tool info for AVR -- Abstractly Verifying Reachability
    """

    REQUIRED_PATHS = ["build/"]

    def executable(self, tool_locator):
        return tool_locator.find_executable("avr.py")

    def name(self):
        return "AVR"

    def project_url(self):
        return "https://github.com/aman-goel/avr"

    def cmdline(self, executable, options, task, rlimits):
        if rlimits.cputime and "--timeout" not in options:
            # The `--timeout` parameter must be passed to the tool
            # to prevent it from using its default value,
            # which could be shorter than the limit set by BenchExec
            # and cause early termination.
            # Moreover, in practice the tool sometimes terminates itself prematurely
            # even when the exact time limit is passed.
            # To prevent this and ensure the tool utilizes the full time limit,
            # a factor of 2 is applied to the timeout value.
            options += ["--timeout", str(rlimits.cputime * 2)]
        if rlimits.memory and "--memout" not in options:
            options += ["--memout", str(ceil(rlimits.memory / 1000000.0))]
        return [executable] + options + [task.single_input_file]

    def determine_result(self, run):
        """
        @return: status of AVR after executing a run
        """
        for line in run.output[::-1]:
            # skip the lines that do not contain verification result
            if not line.startswith("Verification result:"):
                continue
            if "avr-h" in line:
                return result.RESULT_TRUE_PROP
            elif "avr-v" in line:
                return result.RESULT_FALSE_PROP
        return result.RESULT_ERROR
