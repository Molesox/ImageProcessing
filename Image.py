from utilities import *


class Image:

    def __init__(self, name, dirname):
        self.name = name
        self.dirname = dirname

        self.s_extrema = 8
        self.box = (500, 10, 3700, 2200)
        self.im = cv2.imread(os.path.join(dirname, self.name))

        self.im_shape = np.shape(self.im)
        self.width = self.im_shape[1]
        self.height = self.im_shape[0]

        self.border = self.adjustment()

        self.exp = self.get_exp()
        self.iter = self.get_iter()

        self.contour = self.contour_extraction()
        self.contour_color = self.get_contour_color()

        self.leftmost = tuple(self.contour[self.contour[:, :, 0].argmin()][0])
        self.rightmost = tuple(self.contour[self.contour[:, :, 0].argmax()][0])
        self.topmost = tuple(self.contour[self.contour[:, :, 1].argmin()][0])
        self.bottommost = tuple(self.contour[self.contour[:, :, 1].argmax()][0])

        self.extrema = [self.topmost, self.rightmost,
                        self.bottommost, self.leftmost]
        self.extrema_color = self.get_extrema_color()

    def info(self):
        print("Image :{}\n".format(self.name) +
              "location :{}\n".format(self.dirname) +
              " -height : {}\n".format(self.height) +
              " -width : {}\n".format(self.width))
        print("His contour extrema are:\n"
              " -leftmost {}\n".format(self.leftmost) +
              " -rightmost {}\n".format(self.rightmost) +
              " -topmost {}\n".format(self.topmost) +
              " -bottomost {}".format(self.bottommost))

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
