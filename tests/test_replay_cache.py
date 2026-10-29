"""Safety properties of local replay receipts, including interruption/resume."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from replay_cache import ReplayCache, verify_tasks


def parse(stdout, stderr):
    return [], [], json.loads(stderr)


class ReplayCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.cache = ReplayCache(self.directory, {'verifier': 'one'})
        self.task = {'executable': '/checker', 'executable_identity': {'checker': 'binary-one', 'library': 'library-one'},
                     'state_sha256': 'state', 'record_sha256': 'record', 'prefix': 'prefix',
                     'stdout': 'expected\n', 'report': {'cut': 12}, 'key': 'node'}
        self.success = subprocess.CompletedProcess([], 0, 'expected\n', '{"cut":12}')

    def test_only_successfully_compared_output_is_cached(self):
        with patch('replay_cache.subprocess.run', return_value=self.success) as run:
            self.assertEqual(self.cache.verify(self.task, parse), 'replayed')
            self.assertEqual(self.cache.verify(self.task, parse), 'cached')
            self.assertEqual(run.call_count, 1)
        receipt = next(self.directory.rglob('*.json'))
        receipt.write_text('{interrupted')
        with patch('replay_cache.subprocess.run', return_value=self.success) as run:
            self.assertEqual(self.cache.verify(self.task, parse), 'replayed')
            run.assert_called_once()

    def test_input_binary_library_and_verifier_changes_invalidate(self):
        with patch('replay_cache.subprocess.run', return_value=self.success):
            self.cache.verify(self.task, parse)
        changed = []
        for field in ('prefix', 'record_sha256', 'state_sha256'):
            task = copy.deepcopy(self.task)
            task[field] += '-changed'
            changed.append(task)
        for component in ('checker', 'library'):
            task = copy.deepcopy(self.task)
            task['executable_identity'][component] += '-changed'
            changed.append(task)
        with patch('replay_cache.subprocess.run', return_value=self.success) as run:
            for task in changed:
                self.assertEqual(self.cache.verify(task, parse), 'replayed')
            newer = ReplayCache(self.directory, {'verifier': 'two'})
            self.assertEqual(newer.verify(self.task, parse), 'replayed')
            self.assertEqual(run.call_count, len(changed) + 1)

    def test_changed_expectation_cannot_reuse_old_receipt(self):
        with patch('replay_cache.subprocess.run', return_value=self.success):
            self.cache.verify(self.task, parse)
        for field, value in [('stdout', 'different\n'), ('report', {'cut': 13})]:
            task = dict(self.task, **{field: value})
            with patch('replay_cache.subprocess.run', return_value=self.success) as run:
                with self.assertRaises(RuntimeError):
                    self.cache.verify(task, parse)
                run.assert_called_once()

    def test_failure_or_mismatch_never_creates_receipt(self):
        with patch('replay_cache.subprocess.run', side_effect=subprocess.CalledProcessError(1, '/checker')):
            with self.assertRaises(subprocess.CalledProcessError):
                self.cache.verify(self.task, parse)
        for stdout, stderr in [('wrong\n', '{"cut":12}'), ('expected\n', '{"cut":13}')]:
            with patch('replay_cache.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout, stderr)):
                with self.assertRaises(RuntimeError):
                    self.cache.verify(self.task, parse)
        self.assertEqual(list(self.directory.rglob('*.json')), [])

    def test_adaptive_terminal_requires_exhaustion_and_no_graphs(self):
        task = dict(self.task, mode='adaptive-terminal', prefix='26 5 30',
                    stdout='', report={'kind': 26, 'patterns': 0, 'residues': 0})
        report = dict(kind=26, nodes=0, patterns=0, leaves=0, covers=0,
                      filtered=0, residues=0, isomorphism_covers=0, cpu_seconds=0.1)
        # A propagated contradiction can return before incrementing nodes.
        log = 'TEMPLATE_RESULT ' + json.dumps(report) + '\n'
        failures = [('graph6\n', log), ('', ''), ('', log + log)]
        for change in ({'patterns': 1}, {'residues': 1}, {'kind': 25}, {'leaves': -1},
                       {'covers': True}):
            failures.append(('', 'TEMPLATE_RESULT ' + json.dumps(dict(report, **change))))
        for stdout, stderr in failures:
            with self.subTest(stdout=stdout, stderr=stderr):
                with patch('replay_cache.subprocess.run', return_value=
                           subprocess.CompletedProcess([], 0, stdout, stderr)):
                    with self.assertRaises(RuntimeError):
                        self.cache.verify(task, parse)
        self.assertEqual(list(self.directory.rglob('*.json')), [])
        with patch('replay_cache.subprocess.run', return_value=
                   subprocess.CompletedProcess([], 0, '', log)) as run:
            self.assertEqual(self.cache.verify(task, parse), 'replayed')
            self.assertEqual(run.call_args.args[0], ['/checker', 'run'])
            self.assertEqual(self.cache.verify(task, parse), 'cached')

    def test_time_budget_preserves_completed_work(self):
        tasks = [dict(self.task, prefix=str(i)) for i in range(4)]
        def slow(*args, **kwargs):
            time.sleep(0.03)
            return self.success
        with patch('replay_cache.subprocess.run', side_effect=slow):
            partial = verify_tasks(tasks, self.cache, parse, workers=1, seconds=0.01)
        self.assertFalse(partial['complete'])
        self.assertEqual(partial['replayed'], 1)
        with patch('replay_cache.subprocess.run', return_value=self.success) as run:
            resumed = verify_tasks(tasks, self.cache, parse, workers=2)
        self.assertTrue(resumed['complete'])
        self.assertEqual(resumed['cached'], 1)
        self.assertEqual(run.call_count, 3)


if __name__ == '__main__':
    unittest.main()
