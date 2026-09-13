import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools/o_git_completed_merge_guard.py'
spec = importlib.util.spec_from_file_location('merge_guard', SOURCE)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class CompletedMergeGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.root / 'tracked').write_text('base\n')
        self.git('add', 'tracked')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.merge_file = self.root / '.git/MERGE_HEAD'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def test_no_merge_is_noop(self):
        self.assertEqual(guard.completed_merge_guard(self.root)['action'], 'no_merge_metadata')

    def test_completed_merge_and_reappearance_are_cleared_without_data_change(self):
        (self.root / 'tracked').write_text('completed\n')
        self.git('commit', '-qam', 'completed')
        head = self.git('rev-parse', 'HEAD')
        for _ in range(2):
            self.merge_file.write_text(self.base + '\n')
            result = guard.completed_merge_guard(self.root)
            self.assertTrue(result['tracked_data_unchanged'])
            self.assertEqual(self.git('rev-parse', 'HEAD'), head)
            self.assertEqual((self.root / 'tracked').read_text(), 'completed\n')
            self.assertFalse(self.merge_file.exists())

    def test_unfinished_merge_is_preserved(self):
        self.git('checkout', '-qb', 'other')
        (self.root / 'tracked').write_text('other\n')
        self.git('commit', '-qam', 'other')
        other = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-q', self.base)
        self.merge_file.write_text(other + '\n')
        with self.assertRaises(guard.IncompleteMerge):
            guard.completed_merge_guard(self.root)
        self.assertEqual(self.merge_file.read_text().strip(), other)

    def test_uncommitted_work_is_preserved(self):
        self.merge_file.write_text(self.base + '\n')
        (self.root / 'tracked').write_text('unfinished\n')
        with self.assertRaises(guard.IncompleteMerge):
            guard.completed_merge_guard(self.root)
        self.git('add', 'tracked')
        with self.assertRaises(guard.IncompleteMerge):
            guard.completed_merge_guard(self.root)
        self.assertTrue(self.merge_file.exists())
        self.assertEqual((self.root / 'tracked').read_text(), 'unfinished\n')


if __name__ == '__main__':
    unittest.main()
