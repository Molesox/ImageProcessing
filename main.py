from Image import *
from threading import Thread, RLock
import time

verrou0 = RLock()
verrou1 = RLock()
verrou2 = RLock()
verrou3 = RLock()
verrou4 = RLock()


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


# noinspection SpellCheckingInspection
def main():
    clean()
    start_time = time.time()
    nbfiles = nb_files()
    print("Total number of files to analyse: {}".format(nbfiles))

    threads_im = []

    i = 0
    for dirname, dirnames, filenames in os.walk('photos'):
        if i == 0:
            i += 1
            continue

        for filename in filenames:
            threads_im.append(ImGenerator(filename, dirname))

    for thread in threads_im:
        thread.start()

    for thread in threads_im:
        thread.join()
    newfiles = nb_files() - nbfiles
    print("There are {} new files created in : ".format(newfiles) +
          "%s seconds." % (time.time() - start_time))


# noinspection SpellCheckingInspection
def clean():
    for dirname, dirnames, filenames in os.walk('photos'):
        for filename in filenames:
            if filename.startswith('C') or\
                    filename.startswith('E') or\
                    filename.startswith('W') or\
                    filename.startswith('S'):

                os.remove(os.path.join(dirname, filename))


if __name__ == '__main__':
    clean()
