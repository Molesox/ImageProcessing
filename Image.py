import datetime

from utilities import *


class Image:

    def __init__(self, name, dirname, size=(3, 4)):

        self.name = name
        self.dirname = dirname

        self.box = (500, 10, 3700, 2200)
        self.im = cv2.imread(os.path.join(dirname, self.name))

        self.im_shape = np.shape(self.im)
        self.width = self.im_shape[1]
        self.height = self.im_shape[0]
        # self.height += self.adjustment()

        self.irl_width = size[1]
        self.irl_height = size[0]

        self.border = self.adjustment()

        self.exp = self.get_exp()
        self.iter = self.get_iter()

        self.contour = self.contour_extraction()
        self.contour_color = self.get_contour_color()

        self.leftmost = tuple(self.contour[self.contour[:, :, 0].argmin()][0])
        self.rightmost = tuple(self.contour[self.contour[:, :, 0].argmax()][0])
        self.topmost = tuple(self.contour[self.contour[:, :, 1].argmin()][0])
        self.bottommost = tuple(self.contour[self.contour[:, :, 1].argmax()][0])

        self.c_surface = cv2.contourArea(self.contour)
        self.c_perim = cv2.arcLength(self.contour, True)

        self.extrema = [self.topmost, self.rightmost,
                        self.bottommost, self.leftmost]
        self.extrema_color = self.get_extrema_color()
        self.s_extrema = 8

    def info(self):
        to_add = self.adjustment()
        self.leftmost = (self.leftmost[0], self.leftmost[1] + to_add)
        self.rightmost = (self.rightmost[0], self.rightmost[1] + to_add)
        self.topmost = (self.topmost[0], self.topmost[1] + to_add)
        self.bottommost = (self.bottommost[0], self.bottommost[1] + to_add)
        height = self.height + to_add
        f = open(os.path.join(self.dirname, "INFO_" + self.name.replace('.jpg', '') + ".txt"), 'w')
        f.write("Meta données autogénérée {}\n".format(datetime.datetime.now()))
        f.write("Image : {}\n".format(self.name) +
                "location : {}\n".format(self.dirname) +
                " -height : {}, ".format(height) + "{}m\n".format(self.irl_height) +
                " -width : {}, ".format(self.width) + "{}m\n".format(self.irl_width))
        f.write("His contour extrema are:\n"

                " -leftmost {},".format(self.leftmost) +
                " {}cm\n".format(self.to_centimeters(self.leftmost[0], self.leftmost[1])) +

                " -rightmost {},".format(self.rightmost) +
                " {}cm\n".format(self.to_centimeters(self.rightmost[0], self.rightmost[1])) +

                " -topmost {},".format(self.topmost) +
                " {}cm\n".format(self.to_centimeters(self.topmost[0], self.topmost[1])) +

                " -bottomost {},".format(self.bottommost) +
                " {}cm\n".format(self.to_centimeters(self.bottommost[0], self.bottommost[1])) +

                " -area = {}\n".format(self.c_surface) +
                " -perimeter = {}\n".format(self.c_perim))
        f.close()

    def get_extrema_color(self):
        if self.contour_color == (0, 0, 255):
            return 255, 0, 0
        else:
            return 0, 0, 255

    def get_contour_color(self):
        if self.iter == 1:
            return 0, 0, 255
        elif self.iter == 2:
            return 0, 255, 0
        elif self.iter == 3:
            return 255, 0, 0

    def adjustment(self):
        # hard coded... but idk another way
        if self.height > 3000:
            return int((0.2 * self.height) / 2.5)
        else:
            return int((0.5 * self.height) / 2.5)

    def to_centimeters(self, x, y):
        temp_x = x * (self.irl_height / self.height) * 100
        temp_y = y * (self.irl_width / self.width) * 100
        return temp_x, temp_y

    def get_iter(self):
        if self.name.endswith('1.jpg'):
            return 1
        elif self.name.endswith('2.jpg'):
            return 2
        elif self.name.endswith('3.jpg'):
            return 3
        else:
            return -1

    def get_exp(self):
        return self.name[0]

    def contour_extraction(self):
        # define a box to preprocess

        imc = crop(self.im, self.box)

        # transform the image in white black & invert
        im_gray = cv2.cvtColor(imc, cv2.COLOR_BGR2GRAY)
        im_gray = cv2.bitwise_not(im_gray)

        # gaussian filter and adaptive threshold algorithm
        blur = cv2.GaussianBlur(im_gray, (5, 5), 0)
        ret3, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Contours finder without approximation
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Selection of the biggest contour
        tam = 0
        max_cont = 0
        for cont in contours:
            if len(cont) > tam:
                max_cont = cont
                tam = len(cont)

        # to replace the contour according to the box
        for x in max_cont:
            x[0][0] += self.box[0]
            x[0][1] += self.box[1]

        return max_cont

    def print_image_c(self):
        render = self.im
        cv2.drawContours(render, self.contour, -1, self.contour_color, 5)
        cv2.imwrite(os.path.join(self.dirname, "C_" + self.name),
                    render, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def print_image_c_e(self):

        render = self.im
        cv2.drawContours(render, self.contour, -1, self.contour_color, 5)

        for coord in self.extrema:
            change_color(render, coord, self.s_extrema, self.extrema_color)

        cv2.imwrite(os.path.join(self.dirname, "E_C_" + self.name),
                    render, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def print_image_w(self):

        render = create_image(self.width, self.height)
        cv2.drawContours(render, self.contour, -1, self.contour_color, 5)

        render = add_border(render, self.border)

        cv2.imwrite(os.path.join(self.dirname, "W_" + self.name),
                    render, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def print_image_w_e(self):

        render = create_image(self.width, self.height)
        cv2.drawContours(render, self.contour, -1, self.contour_color, 5)

        for coord in self.extrema:
            change_color(render, coord, self.s_extrema, self.extrema_color)

        render = add_border(render, self.border)

        cv2.imwrite(os.path.join(self.dirname, "E_W_" + self.name),
                    render, [cv2.IMWRITE_JPEG_QUALITY, 100])


def print_superposition(images, extrema):
    render = create_image(images[0].width, images[0].height)
    name = 'S_'
    for im in images:
        cv2.drawContours(render, im.contour, -1, im.contour_color, 5)
        if extrema:
            name = 'E_S_'
            for coord in im.extrema:
                change_color(render, coord, im.s_extrema, im.extrema_color)

    render = add_border(render, images[0].border)

    cv2.imwrite(os.path.join(images[0].dirname, name + images[0].dirname.replace('\\', '_') + ".jpg"),
                render, [cv2.IMWRITE_JPEG_QUALITY, 100])
