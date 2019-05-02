from Image import *
from threading import Thread, RLock
import time

verrou0 = RLock()
verrou1 = RLock()
verrou2 = RLock()
verrou3 = RLock()
verrou4 = RLock()
verrou5 = RLock()


class ImGenerator(Thread):

    def __init__(self, filename, dirname):
        Thread.__init__(self)
        self.filename = filename
        self.dirname = dirname
        self.img = 0

    def run(self):
        with verrou0:
            self.img = Image(self.filename, self.dirname)
        with verrou1:
            self.img.print_image_c()
        with verrou2:
            self.img.print_image_c_e()
        with verrou3:
            self.img.print_image_w()
        with verrou4:
            self.img.print_image_w_e()
        with verrou5:
            self.img.info()


# noinspection SpellCheckingInspection
def main():
    clean()
    start_time = time.time()
    nbfiles = nb_files()
    print("Total number of files to analyse: {}".format(nbfiles))

    a = 0
    for dirname, dirnames, filenames in os.walk('photos'):
        if a == 0:
            a += 1
            continue
        l_file = []
        for filename in filenames:
            l_file.append(Image(filename, dirname))
        print_superposition(l_file, False)

    dirnam = []
    threads_im = []
    threads_im2 = []

    tab_thread(dirnam)

    for i in range(0, 16):
        threads_im.append(ImGenerator(dirnam[i][0], dirnam[i][1]))

    for thread in threads_im:
        thread.start()

    for thread in threads_im:
        thread.join()

    threads_im.clear()

    for i in range(16, 34):
        threads_im2.append(ImGenerator(dirnam[i][0], dirnam[i][1]))

    for thread in threads_im2:
        thread.start()

    for thread in threads_im2:
        thread.join()

    threads_im2.clear()

    newfiles = nb_files() - nbfiles
    print("There are {} new files created in : ".format(newfiles) +
          "%s seconds." % (time.time() - start_time))


# noinspection SpellCheckingInspection
def clean():
    for dirname, dirnames, filenames in os.walk('photos'):
        for filename in filenames:
            if filename.startswith('C') or \
                    filename.startswith('E') or \
                    filename.startswith('W') or \
                    filename.startswith('S') or \
                    filename.startswith('INFO'):
                os.remove(os.path.join(dirname, filename))


def tab_thread(filenames_dir):
    i = 0
    for dirname, dirnames, filenames in os.walk('photos'):
        if i == 0:
            i += 1
            continue

        for filename in filenames:
            if filename[0] != 'S':
                filenames_dir.append((filename, dirname))


if __name__ == '__main__':
    main()
