import argparse
import os
from PIL import Image, ImageFont, ImageDraw, ImageOps

class SpriteFontDescription(object):
	def __init__(self, fontname, fontsize, spacing=2, characterRegion=[]):
		self.fontname = fontname
		self.fontsize = fontsize
		self.spacing = spacing
		self.characterRegion = characterRegion

def _findFontFile(fontname, extensions, directories):

	for directory in directories:
		for extension in extensions:
			fullpath = os.path.join(directory, fontname + extension)
			fullpath = os.path.realpath(fullpath)
			print(fullpath)
			if not fullpath:
				continue
			if os.path.exists(fullpath):
				return fullpath

	return None

def loadFont(fontname, size):
	directories = ["", os.path.expanduser("~/Library/Fonts/"), "/Library/Fonts/"]
	extensions = [".ttf", ".otf", ".ttc"]
	filename = _findFontFile(fontname, extensions, directories)
	if not filename:
		raise IOError("Could not found the font named: %s" % fontname)
	return ImageFont.truetype(filename, size * 2)

def drawtext(font, size, ranges, outputname, formatname):
	tileWidth, tileHeight = (int(size * 2.8), int(size * 2.8))
	tile_image = Image.new("RGBA", (4096, 4096), "#ff00ff")

	idx = 0
	spacing = 10
	total = 0
	for start, stop in ranges:
		for char_num in range(start, stop + 1):
			the_char = chr(char_num)

			image = Image.new("RGB", (tileWidth, tileHeight), 0)
			draw = ImageDraw.Draw(image)
			draw.text((0, 0), the_char, font=font, fill="#ffffff")
			crop_image = image.crop(image.getbbox())
			char_width, char_height = crop_image.size
			crop_image = image.crop((0,0,char_width + 4, image.size[1]))

			print("%s => (%d, %d)" % (the_char, char_width, char_height))

			left = spacing
			left += int(idx % 16) * (tileWidth + spacing)

			#left += (tileWidth - char_width) // 2
			upper = spacing
			upper += int(idx / 16) * (tileHeight + spacing)
			#upper += (tileHeight - char_height) // 2

			tile_image.paste(crop_image, (left, upper))
			idx += 1
			total += 1

	lines = total // 16
	if total % 16 != 0:
		lines += 1


	tile_image = tile_image.crop((0,0, spacing + 16 * (tileWidth + spacing),spacing + lines * (tileHeight + spacing)))
	tile_image.save("%s.%s" % (outputname, formatname), formatname)

def valid_int(value):
	if type(value) is int:
		return value
	elif type(value) is str:
		if value.startswith("0x"):
			return int(value, 0)
	else:
		raise Exception("Invalid argument: %s" % value)

def genCharacterRangeList(ranges):
	result = []

	for index in range(0, len(ranges), 2):
		start, stop = (ranges[index], ranges[index + 1])
		if start > stop:
			raise Exception("Invalid range {0}, start must be inferior to stop".format((start, stop)))
		result.append((start, stop))
	return result


def main():
	parser = argparse.ArgumentParser(description="generate a spriteFont from the givent font")
	parser.add_argument("fontname", help="font to use in order to generate the sprite")
	parser.add_argument("-s", dest="size", metavar="size", type=int,help="size of the font")
	parser.add_argument("-sp", dest="spacing", metavar="spacing", type=int, default=2, help="spacing between characters")
	parser.add_argument("ranges", type=valid_int, nargs="+")
	parser.add_argument("-o", dest="output", metavar="output", default="output")
	parser.add_argument("-f", dest="format", metavar="format", default="bmp")
	args = parser.parse_args()

	if len(args.ranges) % 2 != 0:
		raise Exception("Range must be contain a pair number of value")
	ranges = genCharacterRangeList(args.ranges)

	font = loadFont(args.fontname, args.size)
	drawtext(font, args.size, ranges, args.output, args.format)

if __name__ == '__main__':
	main()