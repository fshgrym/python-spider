#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author:fsh
#time:'2018/1/19 20:13:06下午'
# tessdata_dir_config = "--tessdata-dir 'D:\\Tesseract-OCR\\tessdata'"
import pytesseract
from PIL import Image
with Image.open('3.png') as i:
    # pytesseract.image_to_string(i, config=tessdata_dir_config)
    vcode = pytesseract.image_to_string(i)
    print (vcode)