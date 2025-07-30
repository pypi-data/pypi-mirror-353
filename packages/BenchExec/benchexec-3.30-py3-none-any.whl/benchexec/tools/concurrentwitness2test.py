# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0
import benchexec.result as result
import benchexec.tools.template
from benchexec.tools.sv_benchmarks_util import (
    handle_witness_of_task,
    TaskFilesConsidered,
)


class Tool(benchexec.tools.template.BaseTool2):
    """
    Tool info for ConcurrentWitness2Test: A violation witness validator for concurrent programs
    """

    def executable(self, tool_locator):
        return tool_locator.find_executable("start.sh")

    def name(self):
        return "ConcurrentWitness2Test"

    def project_url(self):
        return "https://github.com/ftsrg/ConcurrentWitness2Test"

    def version(self, executable):
        return self._version_from_tool(executable)

    def cmdline(self, executable, options, task, rlimits):
        input_file, witness_options = handle_witness_of_task(
            task, options, "--witness", TaskFilesConsidered.SINGLE_INPUT_FILE
        )
        return [executable] + input_file + options + witness_options

    def determine_result(self, run):
        for line in run.output:
            if "Verdict: SOMETIMES" in line or "Verdict: ALWAYS" in line:
                return result.RESULT_FALSE_REACH
            elif "Verdict: NEVER" in line:
                return result.RESULT_ERROR + "(ineffective witness)"
            elif "Verdict: TIMEOUT" in line:
                return result.RESULT_TIMEOUT + "(inner)"
            elif "Verdict: Unknown error" in line:
                return result.RESULT_ERROR
            elif "Verdict: " in line:
                return result.RESULT_ERROR + "(" + line[len("Verdict: ") :] + ")"

        return result.RESULT_UNKNOWN
