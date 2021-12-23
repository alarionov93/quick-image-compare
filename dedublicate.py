from compare import compare, compare_new, getthumb, MIN, NotAnImage
from shutil import move
from multiprocessing import Process, Queue

import sys
import os

def scan_dir(_dir):
    r = []
    for path, dirs, files in os.walk(_dir):
        if dirs:
            dirs.pop()
        for f in [ "%s%s" % (path, f) for f in files]:
            try:
                # print(f)
                r += [(f, getthumb(f))]
            except NotAnImage:
                pass
    return r
    
def prl_compare(q_in, q_out):
    scanned = []
    while True:
        try:
            f, thumb = q_in.get()
            scanned += [(f, thumb)]
        except ValueError:
            break

    checked = []
    for k1, v1 in scanned:
        print('Checking %s' % k1, end=' ... ', flush=1)
        for k2, v2 in scanned:
            to_check = set([k1,k2])
            if k1 != k2 and to_check not in checked:
                checked += [to_check]
                # q_out.put(to_check)


def prl_scan_dir(_dir, q):
    n = 0
    for path, dirs, files in os.walk(_dir):
        if dirs:
            dirs.pop()
        for f in [ "%s%s" % (path, f) for f in files]:
            try:
                q.put((f, getthumb(f)))
                if not n % 100: print(n, f)
                n += 1
            except NotAnImage:
                pass
    q.put((False,))

def compare_images(scanned, minv):
    checked = []
    res = []
    for k1, v1 in scanned:
        print('Checking %s' % k1, end=' ... ', flush=1)
        nnn = 0
        for k2, v2 in scanned:
            to_check = set([k1,k2])
            if k1 != k2 and to_check not in checked:
                nnn += 1
                x = compare(v1[0], v2[0])
                checked += [to_check]
                if x < minv:
                    res += [(k1, k2, x)]
                    
                    # try:
                    #     if get_biggest_shape(v1[1], v2[1]) == 1:
                    #         to_mv = k2
                    #         print('To_mv=2', v2[1], k2)
                    #     else:
                    #         to_mv = k1
                    #         print('To_mv=1', v1[1], k1)
                    # except IndexError:
                    #     print('Check type of scanned elements: should be tuple!')
                    # res += [(to_mv, x)]
        print(nnn)


    r = sorted(res, key=lambda elem: elem[2])
    with open('aaa.html', 'w') as f:
        f.write('<table>\n')
        for a, b, c in r:
            f.write('<tr><td><img src=\"%s\" style=\"width: 300px;\"></td><td><img src=\"%s\" style=\"width: 300px;\"></td><td>%s</td></tr>\n' % (a,b,c))
        f.write('</table>')

    return r

def get_biggest_shape(shape1, shape2):
    max_w = 0
    nax_h = 0
    if shape1[0]*shape1[1] > shape2[0]*shape2[1]:
        max_val = 1
    else:
        max_val = 2

    return max_val
    
def move_images(compared, _dir):
    for f, f2, x in compared:
        ff = "%s" % os.path.basename(f)
        # print('move(%s, "./moved/"%s)' % (f, ff), end=' ... ', file=sys.stderr)
        try:
            move(f, _dir+ff)
            print('done', file=sys.stderr)
        except OSError:
            print('already moved?', file=sys.stderr)
    
if __name__ == '__main__':
    try:
        file_queue = Queue()
        pairs_queue = Queue()
        scan_proc = Process(target=prl_scan_dir, args=(sys.argv[1], file_queue))
        pair_proc = Process(target=prl_compare, args=(file_queue, pairs_queue))
        # scan_proc = Process(target=prl_scan_dir, args=(sys.argv[1], file_queue))
        for p in [scan_proc, pair_proc]:
            p.start()
        for p in [scan_proc, pair_proc]:
            p.join()
        # imgs_all = compare_images(MIN)
        # move_images(imgs_all, '%s/moved/' % sys.argv[1])
    except IndexError as e:
        print(e)
        print(""" USAGE:
dedublicate /path/

this will move all dublicates of images in path (incl subdirs)
into /tmp/

files will be renamed as '(x) original_name.ext' where x is
tolerance value for debug purposes.
""")