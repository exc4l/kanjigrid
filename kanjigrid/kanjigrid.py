from PIL import Image, ImageDraw, ImageFont
import os
from collections import Counter
from math import ceil


def greet():
    print("hey")
    return "hey"


def load_font(fontpath, fontsize):
    if fontpath == "Kanji":
        # do fancy font loader here
        pass
    elif fontpath == "Header":
        pass
    else:
        return ImageFont.truetype(fontpath, size=fontsize)


class Gridder(object):
    """docstring for Gridder"""

    def __init__(
        self,
        kanjifontpath,
        kanjifontsize,
        headerfontpath,
        headerfontsize,
        colordict=None,
    ):
        super(Gridder, self).__init__()
        self.kfont = load_font(kanjifontpath, kanjifontsize)
        self.hfont = load_font(headerfontpath, headerfontsize)
        self.ksize = kanjifontsize
        self.hsize = headerfontsize
        if colordict is None:
            self.colordict = {
                1: "#cc3232",
                2: "#db7b2b",
                3: "#e7b416",
                4: "#99c140",
                5: "#2dc937",
            }
        else:
            self.colordict = colordict
        # i might want to use a more restricted set as this also contains hanzi
        self.all_kanji_set = set(
            chr(uni) for uni in range(ord("一"), ord("龯") + 1)
        ) | set("〆々")
        self.kcounter = Counter()
        self.background_color = "#FFFFFF"
        self.font_color = "#000000"
        self.padding_above_header = 30
        self.padding_under_header = 50
        self.grid_side_padding = (kanjifontsize,)
        self.columns = 50
        self.bar_horz_border = 2
        self.bar_vert_border = 1

    def _clean_text(self, uctext):
        return "".join(filter(self.all_kanji_set.__contains__, uctext))

    def _get_vert_cat(self, im1, im2):
        res = Image.new("RGB", (im1.width, im1.height + im2.height))
        res.paste(im1, (0, 0))
        res.paste(im2, (0, im1.height))
        return res

    def _get_hori_cat(self, im1, im2):
        res = Image.new("RGB", (im1.width + im2.width, im1.height))
        res.paste(im1, (0, 0))
        res.paste(im2, (im1.width, 0))
        return res

    def _generate_kanji_picto(self, kan, fc=None, bgc=None):
        if bgc is None:
            bgc = self.background_color
        if fc is None:
            fc = self.font_color
        picto = Image.new("RGB", (self.ksize, self.ksize), color=bgc)
        kandraw = ImageDraw.Draw(picto)
        if self.kfont.font.family == "Noto Sans JP":
            kandraw.text((0, -self.ksize / 3.5), kan, font=self.kfont, fill=fc)
        else:
            kandraw.text((0, 0), kan, font=self.kfont, fill=fc)
        return picto

    def _generate_header(self, title, fc=None, bgc=None):
        if bgc is None:
            bgc = self.background_color
        if fc is None:
            fc = self.font_color
        width = self.ksize * self.columns
        head = Image.new("RGB", (width, self.hsize), color=self.background_color)
        pad_bot = Image.new(
            "RGB", (width, self.padding_under_header), color=self.background_color
        )
        pad_top = Image.new(
            "RGB", (width, self.padding_above_header), color=self.background_color
        )
        draw = ImageDraw.Draw(head)
        if self.hfont.font.family == "Noto Sans JP":
            draw.text((0, -self.hsize / 3.5), title, font=self.hfont, fill=fc)
        else:
            draw.text((0, 0), title, font=self.hfont, fill=fc)
        head = self._get_vert_cat(pad_top, head)
        head = self._get_vert_cat(head, pad_bot)

        return head

    def feed_text(self, uctext):
        self.kcounter.update(self._clean_text(uctext))

    def dry_grid(self, grading):
        # col = self.grid_settings["columns"]
        # padtop = self.grid_settings["padding_above_header"]
        # padbot = self.grid_settings["padding_under_header"]
        # sidepad = self.grid_settings["grid_side_padding"]
        # tot width = 2*sidepad + ksize*columns
        # header1 = (padtop+padbot+self.hsize)
        # kanji1 = math.ceil((Anzahl Kanji)/col) * ksize
        pass

    def _generate_subgrid(self, grade):
        grade = sorted(list(grade))
        width = self.ksize * self.columns
        height = self.ksize * (ceil(len(grade) / self.columns))
        img = Image.new("RGB", (width, height), color=self.background_color)
        for k in range(len(grade)):
            kanji = grade[k]
            kcount = self.kcounter.get(kanji, 0)
            if kcount >= max(self.colordict.keys()):
                kanjipic = self._generate_kanji_picto(
                    kanji, bgc=self.colordict[max(self.colordict.keys())]
                )
            else:
                kanjipic = self._generate_kanji_picto(
                    kanji, bgc=self.colordict.get(kcount, self.background_color)
                )
            img.paste(
                kanjipic,
                (k * self.ksize % width, (k * self.ksize // width) * self.ksize),
            )
        return img

    def _generate_stats(self, grading):
        width = self.ksize * self.columns
        img = Image.new("RGB", (self.ksize * self.columns, 0))
        head = self._generate_header("Kanji Stats:")
        for key in sorted(list(self.colordict.keys()), reverse=True):
            tempimg = Image.new("RGB", (width, self.hsize), color=self.background_color)
            if key == max(self.colordict.keys()):
                statstr = f"{key}+ occurrences: "
                statstr += str(sum(k >= key for k in self.kcounter.values()))
            else:
                statstr = f"{key} occurrences: "
                statstr += str(sum(k == key for k in self.kcounter.values()))
            draw = ImageDraw.Draw(tempimg)
            draw.text((self.hsize, 0), statstr, font=self.hfont, fill=self.font_color)
            img = self._get_vert_cat(img, tempimg)
        img = self._get_vert_cat(head, img)
        grade_kanji = grading.get_all_in_grading()
        zero_occ = len(grade_kanji.difference(self.kcounter.keys()))
        occ_percen = 100 * (len(grade_kanji) - zero_occ) / len(grade_kanji)
        temp_str = f"0 occurrences: {zero_occ} " f"({occ_percen:.2f}% occurred)"
        tempimg = Image.new("RGB", (width, self.hsize), color=self.background_color)
        draw = ImageDraw.Draw(tempimg)
        draw.text((self.hsize, 0), temp_str, font=self.hfont, fill=self.font_color)
        img = self._get_vert_cat(img, tempimg)
        return img

    def _generate_outside(self, grading):
        width = self.ksize * self.columns
        head = self._generate_header("Outside of Grading:")
        out_kanji = {k for k in self.kcounter.keys() if not grading.is_in_grading(k)}
        subgrid = self._generate_subgrid(out_kanji)
        concat = self._get_vert_cat(head, subgrid)
        return concat

    def _generate_bar_graph(self, grading):
        width = self.ksize * self.columns - 2 * self.bar_vert_border
        grade_kanji = grading.get_all_in_grading()
        splits = dict()
        for key in sorted(list(self.colordict.keys()), reverse=True):
            if key == max(self.colordict.keys()):
                splits[key] = sum(
                    self.kcounter[k] >= key
                    for k in self.kcounter.keys()
                    if grading.is_in_grading(k)
                )
            else:
                splits[key] = sum(
                    self.kcounter[k] == key
                    for k in self.kcounter.keys()
                    if grading.is_in_grading(k)
                )
        splits[0] = len(grade_kanji.difference(self.kcounter.keys()))
        factor = width / sum(splits.values())
        for k in sorted(list(splits.keys()), reverse=True):
            splits[k] = int(splits[k] * factor)
            if k == min(splits.keys()):
                splits[k] = splits[k] + (width - sum(splits.values()))
        bar = Image.new("RGB", (0, self.ksize))
        for k in sorted(list(splits.keys()), reverse=True):
            part = Image.new(
                "RGB",
                (splits[k], self.ksize),
                color=self.colordict.get(k, self.background_color),
            )
            bar = self._get_hori_cat(bar, part)
        pad = Image.new(
            "RGB",
            (width + 2 * self.bar_vert_border, self.padding_above_header),
            color=self.background_color,
        )
        horz_border = Image.new(
            "RGB",
            (width + 2 * self.bar_vert_border, self.bar_horz_border),
            color=self.font_color,
        )
        vert_border = Image.new(
            "RGB", (self.bar_vert_border, self.ksize), color=self.font_color
        )
        bar = self._get_hori_cat(vert_border, bar)
        bar = self._get_hori_cat(bar, vert_border)
        bar = self._get_vert_cat(horz_border, bar)
        bar = self._get_vert_cat(bar, horz_border)
        bar = self._get_vert_cat(pad, bar)
        # bar = self._get_vert_cat(bar, pad)
        return bar

    def make_grid(
        self,
        grading,
        outside_of_grading=False,
        stats=False,
        bar_graph=False,
    ):
        grid = Image.new("RGB", (self.ksize * self.columns, 0))
        for key in grading.gradings.keys():
            title = grading.gradings[key]["Name"]
            kanjis = grading.gradings[key]["Kanji"]
            head = self._generate_header(title)
            subgrid = self._generate_subgrid(kanjis)
            concat = self._get_vert_cat(head, subgrid)
            grid = self._get_vert_cat(grid, concat)
        if bar_graph:
            img = self._generate_bar_graph(grading)
            grid = self._get_vert_cat(grid, img)
        if outside_of_grading:
            img = self._generate_outside(grading)
            grid = self._get_vert_cat(grid, img)

        if stats:
            img = self._generate_stats(grading)
            grid = self._get_vert_cat(grid, img)
        pad_sides = Image.new(
            "RGB", (self.ksize, grid.height), color=self.background_color
        )
        grid = self._get_hori_cat(grid, pad_sides)
        grid = self._get_hori_cat(pad_sides, grid)
        pad_bottom = Image.new(
            "RGB", (grid.width, self.padding_under_header), color=self.background_color
        )
        grid = self._get_vert_cat(grid, pad_bottom)
        return grid
