#!/usr/bin/env python
'''
	This file is an implementation of Institute of Biblio-Immunology's First Communique
	(see https://pastebin.com/raw/E1xgCUmb)

	It removes the various manifestations of BooXtream's 'Social DRM' from ePub files.
	
	The seven DRM trackers that are removed are as such:

	"WM0-2 are overt (readily visible) watermarks and are optional (meaning they
	may not necessarily be present):

	[WM0] -- Ex Libris Image Watermark
	[WM1] -- Disclaimer Page Watermark
	[WM2] -- Footer Watermarks

	WM3-6 are covert (not readily visible) watermarks and are always present:

	[WM3] -- Filename Watermarks
	[WM4] -- Timestamp Fingerprinting
	[WM5] -- CSS Watermark
	[WM6] -- Image Metadata Watermarks"
'''

from __future__ import unicode_literals
import os
import shutil
import sys, getopt
import six
import zipfile
import hashlib
from bs4 import BeautifulSoup as bs
from wand.image import Image

baseUrl = ".tmp/"
prefix = ""

def cure_bin(u): return u.encode('utf-8') if isinstance(u, six.text_type) else u
def cure_txt(b): return b.decode('utf-8') if isinstance(b, six.binary_type) else b

if six.PY2:
	cure_str = cure_bin
	def cure_2txt(d): return unicode(d)
else:
	cure_str = cure_txt
	def cure_2txt(d): return str(d)

def cure_2bin(d): return cure_2txt(d).encode('utf-8')

def wm0(entry):
	global prefix
	print('\n\n === Removing \'Ex Libris\' watermark (WM0) === \n\n')

	# Set prefix as the root ePub directory; makes files relative to cwd
	print(entry)
	if "/" in entry:
		prefix = os.path.join(entry.split("/")[0])

	cover = open(entry).read()
	soup = bs(cover, "html.parser")

	# Get filename of exlibris watermark
	exlibrispage = soup.find("item", id="exlibrispage") 
	print(exlibrispage)
	if exlibrispage is not None:
		exlibrispage_filename =  dict(exlibrispage.attrs)['href']
		os.remove(os.path.join(prefix, exlibrispage_filename))
		references = searchDirectoryForString('.', "exlibrispage")
		for reference in references:
			soup, tags = findAttrInFile(reference, "exlibrispage")
			removeTagsFromFile(reference, soup, tags)
	else:
		print('\nEx Libris watermark not found')

	# Get filename of exlibris watermark
	exlibris = soup.find("item", id="exlibris") 
	print(exlibris)
	if exlibris is not None:
		exlibris_filename =  dict(exlibris.attrs)['href']
		os.remove(os.path.join(prefix, exlibris_filename))
		references = searchDirectoryForString('.', "exlibris")
		for reference in references:
			soup, tags = findAttrInFile(reference, "exlibris")
			removeTagsFromFile(reference, soup, tags)

		# Get rid of BooXtream tags as well
		references = searchDirectoryForString('.', "BooXtream")
		for reference in references:
			soup, tags = findAttrInFile(reference, "BooXtream")
			removeTagsFromFile(reference, soup, tags)
	else:
		print('\nEx Libris watermark not found')
	print('\nOK')

def wm1():
	global prefix
	print('\n\n === Removing \'Disclaimer\' watermark (WM1) === \n\n')
	disclaimer = ""
	for root, dirnames, filenames in os.walk("."):
		for filename in filenames:
			if "disclaimer" in filename:
				print("[wm1] Found disclaimer file: {0}".format('/'.join([root, filename])))
				disclaimer = '/'.join([root, filename])
	if disclaimer == "":
		print('\nNo Disclaimer file found')
		return
	references = searchDirectoryForString('.', disclaimer)
	for reference in references:
		soup, tags = findAttrInFile(reference, disclaimer)
		removeTagsFromFile(reference, soup, tags)
	os.remove(disclaimer)
	print('\nOK')

def wm2():
	global prefix
	print('\n\n === Removing \'licensing\' watermark (WM2) === \n\n')
	references = set(searchDirectoryForString('.', "is licensed to"))
	references.update(searchDirectoryForString('.', "belongs to"))
	for reference in references:
		soup, tags = findTagsInFile(reference)
		for tag in tags:
			if len(tag.findChildren()) == 0: # No <p> with other <p> inside them
				text_tag = cure_2txt(tag)
				if "is licensed to" in text_tag or "belongs to" in text_tag:
					print("Found match in file: {0}".format(tag))
					removeTagFromFile(reference, soup, tag)
	print('\nOK')

def wm3(entry):
	global prefix
	print('\n\n === Removing \'filename\' watermark (WM3) === \n\n')
	handler = open(entry).read()
	soup = bs(handler, "html.parser")
	items = soup.findAll("item")
	for item in items:
		rand_name = deterministicNameGen()
		href = dict(item.attrs)['href']
		filetype = href.split('.')[-1]
		rand_name += '.'
		rand_name += filetype
		href_path = ""
		if "/" in href:
			href_path = '/'.join(href.split("/")[:-1])
			href = ''.join(href.split("/")[-1])
		new_url = os.path.join(href_path, rand_name)
		print('[wm3] Renaming {0} to {1}'.format(href, new_url))
		references = searchDirectoryForString('.', href)
		for reference in references:
			replaceStringInFile(reference, href.split("/")[-1], rand_name.split("/")[-1])
		renameFile(os.path.join(prefix, href_path, href), os.path.join(prefix, href_path, rand_name))
	print('\nOK')

def wm4():
	print('\n\n === Removing \'timestamp\' watermark (WM4) === \n\n')
	# Timestamp WM - taken care of when unzipping / repackaging :-)
	# Warning: the new timestamps come from when the file is built,
	# contributing a fingerprint to the files.
	print('\nOK')

def wm5():
	global prefix
	print('\n\n === Removing \'boekstaaf\' watermark (WM5) === \n\n')
	css_path = ""
	for root, dirnames, filenames in os.walk("."):
		for filename in filenames:
			if ".css" in filename:
				print("[wm5] Found CSS file: {0}".format(filename))
				css_path = ''.join([root, "/", filename])
	f = open(css_path, "r")
	tmp = ""
	for line in f:
		if "boekstaaf" not in line:
			# force normalize line endings so py3 doesn't stand out
			tmp += line.replace('\r\n', '\n').replace('\r', '\n')
	f.close()
	f = open(css_path, "wb")
	f.write(cure_bin(tmp))
	f.close()
	print('\nOK')

def wm6():
	# Warning: the PNG timestamps can vary between builds, potentially
	# allowing for fingerprinting among "cure" runs.
	print('\n\n === Removing \'exif\' watermark (WM6) === \n\n')
	jpg_paths = []
	png_paths = []
	for root, dirnames, filenames in os.walk("."):
		for filename in filenames:
			if ".jpg" in filename:
				print("[wm6] Found jpg file: {0}".format(filename))
				jpg_paths.append(os.path.join(root, filename))
			if ".png" in filename:
				print("[wm6] Found png file: {0}".format(filename))
				png_paths.append(os.path.join(root,filename))
	for path in jpg_paths:
		print("[wm6] Removing exif from {0}".format(path))
		with Image(filename=path) as img:
			img.strip()
			img.save(filename=path)
	for path in png_paths:
		print("[wm6] Removing metadata from {0}".format(path))
		with Image(filename=path) as img:
			img.strip()
			img.save(filename=path)
	print('\nOK')
	
idx = 0
def deterministicNameGen():
	string = six.b('''We need to take information, wherever it is stored, make our copies and share them with
	the world. We need to take stuff that's out of copyright and add it to the archive. We need
	to buy secret databases and put them on the Web. We need to download scientific
	journals and upload them to file sharing networks. We need to fight for Guerilla Open
	Access.

	With enough of us, around the world, we'll not just send a strong message opposing the
	privatization of knowledge - we'll make it a thing of the past. Will you join us?

	Aaron Swartz
	July 2008, Eremo, Italy
	''')
	global idx
	name = hashlib.md5(six.b('').join([string, cure_2bin(idx)]))
	idx += 1
	return name.hexdigest()[0:20]


def searchDirectoryForString(path, match):
	found = []
	print('[searchDirectoryForString] Searching {0} for {1}'.format(path, match))
	for path, dirs, files in os.walk(path):
		for file in files:
			fullpath = os.path.join(path, file)
			f = open(fullpath, 'rb')
			contents = f.read()
			if cure_bin(match) in contents:
				print('[searchDirectoryForString] Found match in file {0}'.format(fullpath))
				found.append(fullpath)
	return found

def replaceStringInFile(path, match, replace):
	print('[replaceStringInFile] Replacing {0} with {1} in {2}'.format(match, replace, path))
	f = open(path, 'rb').read()
	f = f.replace(cure_bin(match), cure_bin(replace))
	writeToFile(path, f)

def renameFile(path, dst):
	print('[renameFile] Renaming {0} to {1}'.format(path, dst))
	os.rename(path, dst)

def findTagsInFile(path, tag=""):
	f = open(path).read()
	soup = bs(f, "html.parser")
	tags = soup.findAll(tag)
	if tag == "":
		tags = soup.findAll()
	#print '[findTagsInFile] found: {0}'.format(tags)
	return soup, tags

def findAttrInFile(path, match):
	tags = []
	f = open(path).read()
	soup = bs(f, "html.parser")
	for tag in soup.findAll():
		attrs = dict(tag.attrs)
		if match in cure_2txt(attrs):
			print('[findAttrInFile] Found match in {0}'.format(tag))
			tags.append(tag)
	return soup, tags

def removeTagFromFile(path, soup, tags):
	print('[removeTagFromFile] Removing {0} from {1}'.format(tags, path))
	tags.extract()
	writeToFile(path, cure_bin(soup.prettify()))

def removeTagsFromFile(path, soup, tags):
	print('[removeTagsFromFile] Removing {0} from {1}'.format(tags, path))
	for tag in tags:
		tag.extract()
	writeToFile(path, cure_bin(soup.prettify()))


def parseContainer():
	container = "META-INF/container.xml"
	handler = open(container).read()
	soup = bs(handler, "html.parser")
	rootfile = soup.find('rootfile')
	path = dict(rootfile.attrs)['full-path']
	print('[parseContainer] Found entrypoint to ePub:', path)
	return path

def extract(path):
	tmp = zipfile.ZipFile(path)
	tmp.extractall(baseUrl)

def writeToFile(path, content):
	os.remove(path)
	f = open(path, "wb")
	f.write(content)

def buildEpub(path):
	print('\n\n === Rebuilding ePub === \n\n')
	os.chdir("../")
	try:
		os.remove(path)
	except:
		pass
	build = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
	os.chdir(baseUrl)
	print('[buildEpub] Adding mimetype to ePub ...')
	build.write("mimetype")
	for root, dirs, files in os.walk("."):
		for file in files:
			if "mimetype" not in file:
				path = os.path.join(root, file)
				print('[buildEpub] Writing {0} to ePub ...'.format(path))
				zpth = path[len(".")+len(os.sep):]
				build.write(path, zpth)
	os.chdir("..")

def clean():
	print('[clean] Cleaning temporary directory ...')
	shutil.rmtree(baseUrl)

def main(argv):
	infected = ''
	output = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:", ["in=", "out="])
	except getopt.GetoptError:
		print('cure.py -i <infected .epub> -o <destination>')
		sys.exit(2)
	if len(opts) == 0:
		print('cure.py -i <infected .epub> -o <destination>')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print('cure.py -i <infected .epub> -o <destination>')
		if opt in ("-i", "--in"):
			infected = arg
		if opt in ("-o", "--out"):
			output = arg
	print('Curing {0} ...'.format(infected))
	extract(infected)
	os.chdir(baseUrl)
	entry = parseContainer()
	wm0(entry)
	wm1()
	wm2()
	wm3(entry)
	wm4()
	wm5()
	wm6()
	buildEpub(output)
	clean()


if __name__ == "__main__":
	main(sys.argv[1:])
