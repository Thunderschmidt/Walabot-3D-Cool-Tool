# noinspection SpellCheckingInspection
class HeatMapColors:
    """holds the 'heat map' colors information"""

    def __init__(self):
        self.__COLORS = [
            "000080", "000087", "00008B", "00008F", "000093", "000097", "00009B",
            "00009F", "0000A3", "0000A7", "0000AB", "0000AF", "0000B3", "0000B7",
            "0000BB", "0000BF", "0000C3", "0000C7", "0000CB", "0000CF", "0000D3",
            "0000D7", "0000DB", "0000DF", "0000E3", "0000E7", "0000EB", "0000EF",
            "0000F3", "0000F7", "0000FB", "0000FF", "0003FF", "0007FF", "000BFF",
            "000FFF", "0013FF", "0017FF", "001BFF", "001FFF", "0023FF", "0027FF",
            "002BFF", "002FFF", "0033FF", "0037FF", "003BFF", "003FFF", "0043FF",
            "0047FF", "004BFF", "004FFF", "0053FF", "0057FF", "005BFF", "005FFF",
            "0063FF", "0067FF", "006BFF", "006FFF", "0073FF", "0077FF", "007BFF",
            "007FFF", "0083FF", "0087FF", "008BFF", "008FFF", "0093FF", "0097FF",
            "009BFF", "009FFF", "00A3FF", "00A7FF", "00ABFF", "00AFFF", "00B3FF",
            "00B7FF", "00BBFF", "00BFFF", "00C3FF", "00C7FF", "00CBFF", "00CFFF",
            "00D3FF", "00D7FF", "00DBFF", "00DFFF", "00E3FF", "00E7FF", "00EBFF",
            "00EFFF", "00F3FF", "00F7FF", "00FBFF", "00FFFF", "03FFFB", "07FFF7",
            "0BFFF3", "0FFFEF", "13FFEB", "17FFE7", "1BFFE3", "1FFFDF", "23FFDB",
            "27FFD7", "2BFFD3", "2FFFCF", "33FFCB", "37FFC7", "3BFFC3", "3FFFBF",
            "43FFBB", "47FFB7", "4BFFB3", "4FFFAF", "53FFAB", "57FFA7", "5BFFA3",
            "5FFF9F", "63FF9B", "67FF97", "6BFF93", "6FFF8F", "73FF8B", "77FF87",
            "7BFF83", "7FFF7F", "83FF7B", "87FF77", "8BFF73", "8FFF6F", "93FF6B",
            "97FF67", "9BFF63", "9FFF5F", "A3FF5B", "A7FF57", "ABFF53", "AFFF4F",
            "B3FF4B", "B7FF47", "BBFF43", "BFFF3F", "C3FF3B", "C7FF37", "CBFF33",
            "CFFF2F", "D3FF2B", "D7FF27", "DBFF23", "DFFF1F", "E3FF1B", "E7FF17",
            "EBFF13", "EFFF0F", "F3FF0B", "F7FF07", "FBFF03", "FFFF00", "FFFB00",
            "FFF700", "FFF300", "FFEF00", "FFEB00", "FFE700", "FFE300", "FFDF00",
            "FFDB00", "FFD700", "FFD300", "FFCF00", "FFCB00", "FFC700", "FFC300",
            "FFBF00", "FFBB00", "FFB700", "FFB300", "FFAF00", "FFAB00", "FFA700",
            "FFA300", "FF9F00", "FF9B00", "FF9700", "FF9300", "FF8F00", "FF8B00",
            "FF8700", "FF8300", "FF7F00", "FF7B00", "FF7700", "FF7300", "FF6F00",
            "FF6B00", "FF6700", "FF6300", "FF5F00", "FF5B00", "FF5700", "FF5300",
            "FF4F00", "FF4B00", "FF4700", "FF4300", "FF3F00", "FF3B00", "FF3700",
            "FF3300", "FF2F00", "FF2B00", "FF2700", "FF2300", "FF1F00", "FF1B00",
            "FF1700", "FF1300", "FF0F00", "FF0B00", "FF0700", "FF0300", "FF0000",
            "FB0000", "F70000", "F30000", "EF0000", "EB0000", "E70000", "E30000",
            "DF0000", "DB0000", "D70000", "D30000", "CF0000", "CB0000", "C70000",
            "C30000", "BF0000", "BB0000", "B70000", "B30000", "AF0000", "AB0000",
            "A70000", "A30000", "9F0000", "9B0000", "970000", "930000", "8F0000",
            "8B0000", "870000", "830000", "7F0000"]
        self.colors_with_alpha = []
        self.colors = []
        intensity = 0
        for color in self.__COLORS:
            intensity += 1
            tuplecolor = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            self.colors_with_alpha.append((tuplecolor[0], tuplecolor[1], tuplecolor[2], int(intensity)))
            self.colors.append((tuplecolor[0], tuplecolor[1], tuplecolor[2], 255))

    def get(self, value):
        return self.colors_with_alpha[value]

    def get_without_alpha(self, value):
        return self.colors[value]
