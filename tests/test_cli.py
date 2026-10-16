import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(project):
    spec = importlib.util.spec_from_file_location(project.replace('-', '_'), ROOT / 'cli.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectTests(unittest.TestCase):
    def test_all_help_and_invalid_arguments(self):
        for path in [ROOT / 'cli.py']:
            with self.subTest(project=path.parent.name):
                result = subprocess.run([sys.executable, str(path), '--help'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([sys.executable, str(path), '--not-a-real-option'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)

    def test_subtitle_roundtrip_shift_and_rejection(self):
        module = load('subtitle-workbench')
        source = (ROOT / 'examples/demo.srt').read_text()
        vtt = module.convert(source, 'vtt', 500)
        self.assertIn('00:00:01.500 --> 00:00:03.500', vtt)
        restored = module.convert(vtt, 'srt', -500)
        self.assertEqual(module.parse(source), module.parse(restored))
        with self.assertRaises(ValueError):
            module.convert(source, 'srt', -10000)
        with self.assertRaises(ValueError):
            module.parse('1\n00:61:00,000 --> 00:62:00,000\nbad\n')
        with self.assertRaises(ValueError):
            module.parse('WEBVTT\n\n00:01.000 --> 00:02.000 align:start\nhello\n')

if __name__ == '__main__':
    unittest.main()
