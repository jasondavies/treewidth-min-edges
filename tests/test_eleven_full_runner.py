"""The coordinator must never turn failed or incomplete stages into success."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import reproduce_eleven_full as runner


class FullRunnerTests(unittest.TestCase):
    def run_fixture(self, failure=None, bad_summary=False):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base/'genreg'
            source.mkdir()
            for name in runner.GENREG_FILES:
                (source/name).write_text('test source')
            output = base/'output'
            calls = []
            def execute(command, **kwargs):
                if command[0] == 'stage':
                    calls.append(command[1])
                    if command[1] == failure:
                        return subprocess.CompletedProcess(command, 2)
                    for name, report in (
                        ('earlier/summary.json', dict(status='complete', mode='full', minimum_edges=47)),
                        ('girth-five/summary.json', dict(status='complete', completed_parts=256)),
                        ('squares/treewidth11/resumable-quartic/summary.json',
                         dict(status='partial_replay' if bad_summary else 'required_replays_verified',
                              terminal_replays=True, covered_roots=5)),
                    ):
                        path = output/name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(json.dumps(report))
                return subprocess.CompletedProcess(command, 0)
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(sys, 'argv', ['runner', '--genreg-source', str(source),
                                                              '--output', str(output)]))
                stack.enter_context(patch.dict(os.environ, {'PYTHONOPTIMIZE': ''}))
                stack.enter_context(patch.object(runner, 'inventory', return_value={'input': 'hash'}))
                stack.enter_context(patch.object(runner.shutil, 'which', return_value='/bwrap'))
                stack.enter_context(patch.object(runner.subprocess, 'run', side_effect=execute))
                stack.enter_context(patch.object(runner, 'stages', return_value=[
                    (name, ['stage', name]) for name in ('first', 'second', 'third')]))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                if failure or bad_summary:
                    with self.assertRaises(RuntimeError):
                        runner.main()
                else:
                    runner.main()
            return calls, json.loads((output/'summary.json').read_text())

    def test_nonzero_stage_stops_and_cannot_pass(self):
        calls, report = self.run_fixture(failure='second')
        self.assertEqual(calls, ['first', 'second'])
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['stages']['second']['returncode'], 2)

    def test_partial_replay_report_cannot_pass_even_with_zero_exits(self):
        calls, report = self.run_fixture(bad_summary=True)
        self.assertEqual(len(calls), 3)
        self.assertNotEqual(report['status'], 'complete')

    def test_all_stages_and_complete_reports_are_required(self):
        calls, report = self.run_fixture()
        self.assertEqual(calls, ['first', 'second', 'third'])
        self.assertEqual(report['status'], 'complete')


if __name__ == '__main__':
    unittest.main()
