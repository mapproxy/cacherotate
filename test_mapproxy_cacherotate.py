import os
import shutil
import tempfile
from mapproxy_cacherotate import PaddedLevel, SQLiteLevel, main


class TestRotate(object):
    type = PaddedLevel
    args = []

    def setup(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cachedir = os.path.join(self.tmpdir, 'cache')
        os.makedirs(self.cachedir)

    def teardown(self):
        shutil.rmtree(self.tmpdir)

    def make_levels(self, levels):
        for l in levels:
            with open(os.path.join(self.cachedir, self.type(str(l)).next(0)), 'w') as f:
                f.write(str(l))


    def level_file(self, level):
        return os.path.join(self.cachedir, self.type(str(level)).next(0))

    def assert_not_level(self, level):
        assert not os.path.exists(self.level_file(level)), 'level %s exists' % self.level_file(level)

    def assert_level(self, level, was=None):
        level_file = self.level_file(level)
        assert os.path.exists(level_file), 'level %s does not exist' % level_file

        if not was:
            return

        with open(level_file) as f:
            was_level = int(f.read())
            assert was == was_level, 'level %s was %s, not %s' % (level_file, was_level, was)

    def assert_dropped_level(self, level):
        level_file = self.level_file(level) + '.dropped'
        assert os.path.exists(level_file), 'level %s does not exist' % level_file


    def test_rotate_level_end(self):
        self.make_levels([0, 1, 3])

        for _ in range(2):
            main([self.cachedir, '--from-level', '4', '--rotate'] + self.args)

            self.assert_level(0, was=0)
            self.assert_level(1, was=1)
            self.assert_not_level(2)
            self.assert_level(3, was=3)
            self.assert_not_level(4)
            self.assert_not_level(5)

    def test_rotate_level_mid(self):
        self.make_levels([0, 1, 2, 3, 4, 5, 6, 7])

        for _ in range(2):
            main([self.cachedir, '--from-level', '5', '--rotate'] + self.args)

            self.assert_level(0, was=0)
            self.assert_level(1, was=1)
            self.assert_level(2, was=2)
            self.assert_level(3, was=3)
            self.assert_level(4, was=4)
            self.assert_not_level(5)
            self.assert_level(6, was=5)
            self.assert_level(7, was=6)
            self.assert_level(8, was=7)

    def test_rotate_level_missing(self):
        self.make_levels([0, 1, 2, 3, 4, 6, 7])

        for _ in range(2):
            main([self.cachedir, '--from-level', '5', '--rotate'] + self.args)

            self.assert_level(0, was=0)
            self.assert_level(1, was=1)
            self.assert_level(2, was=2)
            self.assert_level(3, was=3)
            self.assert_level(4, was=4)
            self.assert_not_level(5)
            self.assert_not_level(6)
            self.assert_level(7, was=6)
            self.assert_level(8, was=7)

    def test_drop_level_mid(self):
        self.make_levels([0, 1, 2, 3, 4, 5, 6, 7])

        for _ in range(2):
            main([self.cachedir, '--drop-level', '3', '--rotate'] + self.args)

            self.assert_not_level(7)
            self.assert_level(6, was=7)
            self.assert_level(5, was=6)
            self.assert_level(4, was=5)
            self.assert_level(3, was=4)
            self.assert_level(2, was=2)
            self.assert_level(1, was=1)
            self.assert_level(0, was=0)
            self.assert_dropped_level(3)

    def test_drop_level_missing(self):
        self.make_levels([0, 1, 2, 4, 5, 6, 7])

        for _ in range(2):
            main([self.cachedir, '--drop-level', '3', '--rotate'] + self.args)

            self.assert_not_level(7)
            self.assert_level(6, was=7)
            self.assert_level(5, was=6)
            self.assert_level(4, was=5)
            self.assert_level(3, was=4)
            self.assert_level(2, was=2)
            self.assert_level(1, was=1)
            self.assert_level(0, was=0)

    def test_drop_level_0(self):
        self.make_levels([0, 1, 2, 3, 4, 5, 6, 7])

        for _ in range(2):
            main([self.cachedir, '--drop-level', '0', '--rotate'] + self.args)

            self.assert_not_level(7)
            self.assert_level(6, was=7)
            self.assert_level(5, was=6)
            self.assert_level(4, was=5)
            self.assert_level(3, was=4)
            self.assert_level(2, was=3)
            self.assert_level(1, was=2)
            self.assert_level(0, was=1)
            self.assert_dropped_level(0)

class TestRotateSQLite(TestRotate):
    type = SQLiteLevel
    args = ['--type', 'sqlite']