import errno
import time
import os

class PaddedLevel(str):
    def valid(self):
        return self.isdigit()

    def level(self):
        return int(self)

    def next(self, delta):
        return '%02d' % (self.level() + delta)

class SQLiteLevel(str):
    def valid(self):
        return self.endswith('.mbtile') and self[:-len('.mbtile')].isdigit()

    def level(self):
        return int(self.split('.', 1)[0])

    def next(self, delta):
        return '%d.mbtile' % (self.level() + delta)

def main(args=None):
    import optparse
    parser = optparse.OptionParser(usage='%prog [options] cachedir1 cachedir2 ...')
    parser.add_option('--from-level', type=int, default=None)
    parser.add_option('--drop-level', type=int, default=None)
    parser.add_option('--rotate', action='store_true')
    parser.add_option('--type', default='tile')

    parser.add_option('--remove-locks', action='store_true')

    opts, args = parser.parse_args(args)
    if len(args) <= 0:
        parser.print_usage()
        return False

    if not opts.remove_locks:
        if not((opts.drop_level is not None) ^ (opts.from_level is not None)):
            print 'ERROR: need --drop-level or --from-level',
            return False

    if opts.type == 'sqlite':
        cache_type = SQLiteLevel
    elif opts.type == 'tile':
        cache_type = PaddedLevel
    else:
        print 'unknown --type'
        return False

    delta = 1
    if opts.drop_level is not None:
        delta = -1

    if opts.remove_locks:
        for cache_dir in args:
            print 'removing .last_rotate in', cache_dir
            remove_last_rotate_time(cache_dir)
        return True

    for cache_dir in args:
        last = last_rotate_time(cache_dir)
        if not last:
            last = 0
            if opts.rotate:
                update_last_rotate_time(cache_dir)

        print 'rotating', cache_dir
        for src, dst in rotate_levels(cache_dir, opts.from_level or opts.drop_level, cache_type=cache_type, delta=delta, drop_level=opts.drop_level):
            print '  ', src, '->', dst,
            seconds_since_rotate = abs(os.path.getmtime(src) - last)
            if seconds_since_rotate < 10:
                print 'SKIP: already rotated'
                continue
            if opts.rotate:
                rotate_level(src=src, dst=dst, cache_dir=cache_dir)
                print 'DONE'
            else:
                print

    if not opts.rotate:
        print 'NOTE: This was a dry-run. Re-run with --rotate'

    return True

def remove_last_rotate_time(cache_dir):
    try:
        return os.unlink(os.path.join(cache_dir, '.last_rotate'))
    except OSError, ex:
        if ex.errno != errno.ENOENT:
            raise

def last_rotate_time(cache_dir):
    try:
        return os.path.getmtime(os.path.join(cache_dir, '.last_rotate'))
    except OSError, ex:
        if ex.errno != errno.ENOENT:
            raise

def update_last_rotate_time(cache_dir):
    with open(os.path.join(cache_dir, '.last_rotate'), 'w') as f:
        f.flush()

def rotate_level(src, dst, cache_dir):
    # make sure destination does not exists
    assert not os.path.exists(dst)

    os.rename(src, dst)
    os.utime(dst, (time.time(), time.time()))

def rotate_levels(cache_dir, first_level, cache_type, delta, drop_level):
    levels = [cache_type(l) for l in os.listdir(cache_dir)]
    levels = [l for l in levels if l.valid()]

    ordered_levels = sorted(levels, key=lambda x: x.level())
    if delta > 0:
        ordered_levels.reverse()

    for level in ordered_levels:
        if level.level() < first_level:
            continue

        if drop_level is not None and (level.level() == drop_level):
            yield os.path.join(cache_dir, level), os.path.join(cache_dir, level + '.dropped')
        else:
            yield os.path.join(cache_dir, level), os.path.join(cache_dir, level.next(delta))



if __name__ == '__main__':
    main()