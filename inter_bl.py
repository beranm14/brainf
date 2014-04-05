#!/usr/bin/python3
import sys
from optparse import OptionParser
import os
import zlib

#Definice pro getchary a putchary
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)
sys.stdout = Unbuffered(sys.stdout)

class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt
    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

def putchar(n):
	print(chr(n), end='')

def giveSymb(symbol):
	if symbol==(255,0,0,255):
		return(">")
	elif symbol==(128,0,0,255):
		return("<")
	elif symbol==(0,255,0,255):
		return("+")
	elif symbol==(0,128,0,255):
		return("-")
	elif symbol==(0,0,255,255):
		return(".")
	elif symbol==(0,0,128,255):
		return(",")
	elif symbol==(255,255,0,255):
		return("[")
	elif symbol==(128,128,0,255):
		return("]")
	elif symbol==(0,255,255,255):
		return("P")
	elif symbol==(0,128,128,255):
		return("L")
	else:
		return("X")
def load_png_image(image):
    """Return width and height of PNG image

    Args:
        image: reference to PNG file
    Returns:
        (width, height) tuple
    """

    # precte hlavicku obrazku
    head = image.read(8)
    # zkontroluje, ze se jedna o hlavicku PNG obrazku
    assert head == b'\x89PNG\r\n\x1a\n', 'File is not PNG image'

    image.seek(4, 1)  # preskoci IHDR SIZE
    image.seek(4, 1)  # preskoci IHDR TYPE
    # precte sirku obrazku z IHDR data
    width = int.from_bytes(image.read(4), 'big')
    # precte vysku obrazku z IHDR data
    height = int.from_bytes(image.read(4), 'big')

    return width, height

def load_png_data(image, image_properties):
    """Return PNG image pixels

    Args:
        image: reference to PNG file
        image_properties: (width, height) tuple
    Returns:
        list of list of pixels - [[(r, g, b, a), (r, g, b, a) ...]]
    """

    width = image_properties[0]
    height = image_properties[1]
    # preskoci hlavicku obrazku a oznaceni IHDR - 0 znamena, ze se pozice kurzoru nastavuje od zacatku
    image.seek(8 + 8 + 13 + 4, 0)
    # nacte delku dat IDAT chunku
    data_size = int.from_bytes(image.read(4), 'big')
    # preskoci oznaceni chunku b'IDAT'
    image.seek(4, 1)
    # nacte data
    data = image.read(data_size)
    # rozbali data v chunku IDAT
    data = zlib.decompress(data)

    # do seznamu pixels se nactou vsechny radky obrazku
    pixels = []
    for row_index in range(height):
        # do seznamu row se ukladaji jednotlive entice
        # obsahujici podslozky pixelu - r, g, b, alpha channel
        row = []
        # nastaveni pozice na zacatek dalsiho radku
        # kazdy pixel se sklada ze 4 bytu - proto ta ctyrka
        # kazdy radek obsahuje na zacatek typ filtrovani
        # a ten musime preskocit pomoci "+ row_index"
        start = row_index * width * 4 + row_index
        # konec je delka radku + "pocatecni pozice"
        end = start + width * 4
        # inkrementuje se s krokem 4 - pixel obsahuje 4 byty
        for pixel in range(start, end, 4):
            r = data[pixel + 1]
            g = data[pixel + 2]
            b = data[pixel + 3]
            a = data[pixel + 4]
            row.append((r, g, b, a))
        pixels.append(row)
    return pixels


def isPng(inp):
	header = b'\x89PNG\r\n\x1a\n'
	if inp == header:
		return 1
	else:
		return 0

#Parsovani a nacitani
parser = OptionParser(usage="Usage: %prog -f file", version="%prog 0.1")
parser.add_option("-f","--FileName", action="store", dest="filename", type="string", help="Nastaveni jmena vstupniho souboru")

args = sys.argv[1:]
(options, args) = parser.parse_args()
if options.filename:
	if not (os.path.exists(options.filename)):
		print("Soubor neexistuje")
else:
	print("Usage: inter_bl.by -f file.png")
	exit(2);

matr=[]
j=0
maxx=0
maxy=0
with open(options.filename, 'rb') as f:
	image_properties = load_png_image(f)
	pixels = load_png_data(f, image_properties)
	#print(len(pixels))
	for it in pixels:
		matr.append([]);
		maxy=len(it)
		for i in it:
			#print(giveSymb(i),end="")
			matr[j].append(giveSymb(i));
		#print(" r:" + str(j))
		j+=1
maxx=j
#print(matr)
class Patf:
	x=0
	y=0
	v=0
	def turnLeft(self):
		self.v=(self.v-1)%4
		self.step()
	def turnRight(self):
		self.v=(self.v+1)%4
		self.step()
	def step(self):
		if self.v == 0:
			self.x+=1
		elif self.v == 1:
			self.y+=1
		elif self.v == 2:
			self.x-=1
		elif self.v == 3:
			self.y-=1
	def swVec(self):
		if self.v == 0:
			self.v=2
		elif self.v == 1:
			self.v=3
		elif self.v == 2:
			self.v=0
		elif self.v==3:
			self.v=1
ch=Patf()
bftxt=""
# 0 ->
# 1 dolu
# 2 <-
# 3 nahoru
tape=[0]
brstx=[]
brsty=[]
tapepnt=0
o=1

#print("maxy"+str(maxy)+"maxx"+str(maxx));
x=ch.x
y=ch.y
while maxx>y and maxy>x and y>=0 and x>=0:
	if matr[y][x] == "+" :
		tape[tapepnt]+=1
		ch.step()
	elif matr[y][x] == "-" :
		tape[tapepnt]-=1
		ch.step()
	elif matr[y][x] == "." :
		putchar(tape[tapepnt])
		ch.step()
	elif matr[y][x] == "," :
		tape[tapepnt]=ord(getch())
		ch.step()
	elif matr[y][x] == ">" :
		if len(tape) - 1 == tapepnt:
			tape=tape+[0]
		tapepnt+=1
		ch.step()
	elif matr[y][x] == "<" :
		tapepnt-=1
		ch.step()
	elif matr[y][x] == "[" :
		if tape[tapepnt] == 0:
			ch.step()						
			x=ch.x
			y=ch.y
			while o > 0 :
				if matr[y][x] == "[":
					o+=1
					ch.step()
				elif matr[y][x] == "]":
					o-=1
					ch.step()
				elif matr[y][x] == "P":
					ch.turnRight()
				elif matr[y][x] == "L":
					ch.turnLeft()
				else:
					ch.step()						
				x=ch.x
				y=ch.y
			o=1
		elif tape[tapepnt] != 0:
			brstx.append(x)
			brsty.append(y)
			ch.step()
	elif matr[y][x] == "]" :
		#if tape[tapepnt] != 0:
		mx=x
		ch.x=brstx.pop()
		my=y
		ch.y=brsty.pop()

		if my % 2 == 0 and ch.y % 2 == 1 and (ch.v == 0 or ch.v == 2):  # pokud je z lichý na sudý, změň směr, jinak ne
			ch.swVec()
		elif my % 2 == 1 and ch.y % 2 == 0 and (ch.v == 0 or ch.v == 2):
			ch.swVec()
		elif mx % 2 == 0 and ch.x % 2 == 1 and (ch.v == 1 or ch.v == 3):  # pokud je z lichý na sudý, změň směr, jinak ne
			ch.swVec()
		elif mx % 2 == 1 and ch.x % 2 == 0  and (ch.v == 1 or ch.v == 3):
			ch.swVec()
			#ch.swVec()
		#elif tape[tapepnt] == 0:
			#ch.x=brstx.pop()
			#ch.y=brsty.pop()
			#ch.swVec()
	elif matr[y][x] == "P" :
		ch.turnRight()
	elif  matr[y][x] == "L" :
		ch.turnLeft()
	else:
		ch.step()	
	#print("x:" + str(x) + " y:" + str(y) + " v:" + str(ch.v) + " |" + matr[y][x])
	x=ch.x
	y=ch.y




