BooXtream ePub DRM Remover
===

This script is an implementation of Institute of Biblio-Immunology's First Communique:

["Identifying and Removing Verso/BooXtream 'Social DRM' EPUB eBook Watermarks"](https://pastebin.com/raw/E1xgCUmb)

It removes the various manifestations of BooXtream's 'Social DRM' from ePub files.

The seven DRM watermarks that are removed are:
```
"WM0-2 are overt (readily visible) watermarks and are optional (meaning they may not necessarily be present):
  [WM0] -- Ex Libris Image Watermark
  [WM1] -- Disclaimer Page Watermark
  [WM2] -- Footer Watermarks
WM3-6 are covert (not readily visible) watermarks and are always present:
  [WM3] -- Filename Watermarks
  [WM4] -- Timestamp Fingerprinting
  [WM5] -- CSS Watermark
  [WM6] -- Image Metadata Watermarks
  [WM7] -- Ebook.de meta file protection"
```

Installation
===

Python requirements:

```BeautifulSoup4, Wand (both can be installed via pip or easy_install)```

System requirements:

```ImageMagick (used by Wand)``` 


Running
===

```cure.py -i <infected .epub> -o <destination>```
