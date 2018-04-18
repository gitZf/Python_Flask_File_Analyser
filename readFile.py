import json
import os
from distutils import text_file
from flask import session
import re
import nltk
import chardet
import codecs
import hashlib
import app
from flask import Flask, flash, render_template
import PyPDF2
from docx import Document

FILE = 'assosiation.txt'
JFILE = 'json.json'

def read_JSON() -> list:
    """This function read association file and returning list of  the key words"""
    keywords =[]
    with open(JFILE) as data:
        keyList = json.load(data)
    data.close()
    for k, v in keyList.items():
        keywords.append(k)
    return keywords


def load_JSON() -> 'dict':
    """This function read JSON file and returning a Dictionary"""
    keywords = []
    with open(JFILE) as data:
        keywords = json.load(data)
    data.close() 
    return keywords

def getsize(filename):
    """Return the size of a file, reported by os.stat()."""
    return os.stat(filename).st_size/1024

def red_uploaded_file(filename) -> 'list':
    """This method read the uploaded file to server, and change to lower case, remove
    punctuation, slit it, get the 64 bit HEX key and the inputstring"""
    path = 'UPLOAD_FOLDER/' + filename
    dt = chardet.detect(open(path, "rb").read())
    session['printname'] = filename
    if filename.endswith('.txt') or filename.endswith('.json'):
        print('reading txt or json')
        f = open(path,encoding=dt['encoding'])
        raw = f.read()
        print(raw)
        raw = re.sub(r'[^\w\s]',' ',raw)
        raw = raw.lower()
        listWords = raw.split()
        print(listWords)
        f.close()
        inputString = session['inputString'] = raw
        sha_hash = hashlib.sha256(bytes(inputString, encoding=dt['encoding'])).hexdigest()
        #print("SHA" , sha_hash)
        app.store(sha_hash)
        return listWords 
    elif filename.endswith('.pdf'):
        print('reading pdf')
        if dt['encoding'] == None:
            print('cant find encoding')
            return 'STOP'
        else:
            #print('encoding found ', dt['encoding'])
            pdfFileObj = open(path, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            numpage = pdfReader.numPages
            i = 0
            raw =''
            while i < numpage:
                pageObj = pdfReader.getPage(i)
                text = pageObj.extractText()
                raw += text 
                i += 1
            #print(raw)
            raw = re.sub(r'[^\w\s]',' ',raw)
            raw = raw.lower()
            listWords = raw.split()
            inputString = session['inputString'] = raw
            sha_hash = hashlib.sha256(bytes(inputString, encoding=dt['encoding'])).hexdigest()
            app.store(sha_hash)
            return listWords
    elif filename.endswith('.docx'):
        print('reading docx')
        raw =''
        document = Document(path)
        for para in document.paragraphs:
            raw += para.text
        raw = re.sub(r'[^\w\s]',' ',raw)
        raw = raw.lower()
        listWords = raw.split()
        inputString = session['inputString'] = raw
        sha_hash = hashlib.sha256(bytes(inputString, encoding='Latin1')).hexdigest()
        app.store(sha_hash)
        return listWords

        
    
    
    
    
    
    






