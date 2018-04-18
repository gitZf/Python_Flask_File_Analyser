import enchant
import time
import pymongo
import collections
from collections import Counter
from flask import Flask, flash, render_template
from flask import request, session, url_for,abort,redirect
import readFile
import os
import json
from werkzeug.utils import secure_filename
import hashlib
import hmac
import operator
import re
from collections import OrderedDict


UPLOAD_FOLDER = 'UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = set(['txt','json','docx','pdf'])

app = Flask(__name__)



app.secret_key = 'fhdgsd;ohfnvervneroigerrenverbner32hrjegb/kjbvr/o'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_client() -> 'MongoCLient':
    """This function return pymongo client object"""
    client = pymongo.MongoClient()
    db = client['c3']
    c = db['json']
    return c

@app.route('/')
@app.route('/mainpage')
def mainpage() -> 'html':
    """Main page 127.0.0.1:5000"""
    return render_template('mainpage.html',
                           title='Word association')


def check_fileName(session) -> 'bool':
    """This function checking the 64 bit HEX key against the database"""
    c = get_client()
    cursor = c.find({},{"size":1, "_id":0})
    print(session)
    for document in cursor:
        print(document)
        if hmac.compare_digest(session, document["size"]):
            return True
        print("size ", document["size"])
    return False

def render_mainpageerror(errormsg) -> 'html':
    """This methode remove duplicates render template lines"""
    return render_template('mainpage.html',
                                   title='Word association',
                                   analyse=errormsg)

@app.route('/analyse', methods=['POST'])
def analyse() -> 'html':
    """This function is the main checking and analysis"""
    storeFileName = ''
    if request.method == 'POST':
        
        if 'file' not in request.files:
            return render_mainpageerror('No file selected')
 
        file = request.files['file']
        if file.filename == '':
            return render_mainpageerror('Empty file name Please select a File to upload')
        
        if file and not allowed_file(file.filename):
            storeFileName = filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_mainpageerror('Not allowed file format')
        
        if ' ' in file.filename:
            return render_mainpageerror('Please remove withespace from file name before uploading')
        
        if file and allowed_file(file.filename):
            originalFilename = file.filename
            storeFileName = filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
     
    if len(storeFileName) == 0:
        return render_template('mainpage.html',
                               title='Word association')
    else:
        wordsfromfile = readFile.red_uploaded_file(storeFileName)
        #print(wordsfromfile, 'The ans from pdf')
        if wordsfromfile == 'STOP':
            return render_mainpageerror('Cant find Encoding on PDF document')
        size = get_store()
        if not check_fileName(size):
            """Analyse first time building up JSON file"""
            keyWords = readFile.read_JSON()
            allJson = readFile.load_JSON()
            data = Counter(wordsfromfile)
            printResultsExluds = []
            container = {}
            container['size'] = size
            container['file'] = storeFileName
            toDB = []
            for k, v in sorted(data.items()):
                if k in keyWords:
                    string = allJson[k][:3]
                    toDB.append({k : v})
                    toDB.append(string)
                else:
                    value = str(v)
                    keystr = k + '(' + value + ')'
                    printResultsExluds.append(keystr)
            for w in printResultsExluds:
                toDB.append({w:'was not found in the associations list'})

            container['files'] = toDB               
            js = json.dumps(container)
            print(js)
            c = get_client()
            c.insert(json.loads(js))
            print('insert')
            """If analysed first time"""
            return pr(size, 'Analysed first time')
        else:
            """If already Analysed"""
            return pr(size,'Already analysed')

           
@app.route('/previous')
def previous() -> 'html':
    """This function build the previous files dropDown box and then redirect to previous page"""
    fileList = []
    c = get_client()
    cursor = c.find({},{"file":1,"size":1, "_id":0})
    filedict = []
    front = ''
    back = ''
    i = 0
    for k in cursor:
        for key, value in k.items():
            if value != 4 and len(value)>50:
                back = value
                i += 1
            else:
                front = value
                i += 1
            if i == 2:
                dict =( front , back )
                filedict.append(dict)
                i = 0
    if len(filedict) == 0:
        """If no data in the database"""
        dict =( 'Empty DB' , 0 )
        filedict.append(dict)
    return render_template('previous.html',
                           title='Previous files',
                           analyse="",
                           prev=filedict)


@app.route('/reprint', methods=['POST'])
def reprint() -> 'html':
    """This function make dicision which redirecting will be used"""
    size = request.form['name']
    store(size)
    if size == '0':
        """Empty database send back to previous page"""
        return previous()
    else:
        """Selected file redirect to print details"""
        store(size)
        return pr(size,'From database')



def store(value):
    """SESSION function use database to store key, flask NOT good enough to handle session :)"""
    client = pymongo.MongoClient()
    #sessionKey = value
    db = client['c3S']
    c = db['json']
    c.update_one({'_id': 12345},{'$set': {'session': value}}, upsert=False)


def get_store():
    """SESSION function use database to retrieve key, flask NOT good enough to handle session :)"""
    session = 4
    client = pymongo.MongoClient()
    db = client['c3S']
    c = db['json']
    sess = 0
    cursor = c.find({},{ 'session' : 1,'_id':0})
    for w in cursor:
        sess = w['session']
        print("Found " , sess)
        print("SESSION valu is ", session)
    return sess

def pr(size, analys) -> 'html':
    """This function build up output to screen when uploading file"""
    c = get_client()
    fileName = ''
    store(size)
    cursor = c.find({ 'size' : size })
    listF = []
    add = 0
    for line in cursor:
        fileName = line['file']
        for f in line['files']:
            if isinstance(f, dict):
                for k ,v in f.items():
                    strin = k + ' (' + str(v) + ') '
                    add += 1
            else:
                strin += str(f)
                add += 1
            if add == 2:
                listF.append(strin)
                add = 0
           
    listOrder = []
    listOrder.append('A-Z')
    listOrder.append('Occurance')
    if analys == 'Analysed first time':
        return render_analysis('mainResult.html',analys,fileName,listF,listOrder)
    else:
        return render_analysis('reprint.html',analys,fileName,listF,listOrder)

def render_analysis(page,analys,fileName,listF,listOrder) -> 'html':
    """This methode remove duplicate render template lines"""
    return render_template(page,
                               title='Analysis',
                               n=analys + ' '+ fileName,
                               fileList=listF,
                               prev = listOrder)

@app.route('/reprintOrder', methods=['POST'])
def reprintOrder() -> 'html':
    """This function create a list by A-Z or by occurance, build output by order"""
    name = request.form['order']
    c = get_client()
    size = get_store()
    filename =''
    cursor = c.find({ 'size' : size })
    listF = []
    newL = []
    dictD = OrderedDict()
    orderedList = ()
    lf = []
    dickKey = ''
    dictValue = ''
    add = 0
    for line in cursor:
        fileName = line['file']
        if name == 'A-Z':
            for f in line['files']:
                if isinstance(f, dict):
                    for k ,v in f.items():
                        strin = k + ' (' + str(v) + ') '
                        add += 1
                else:
                    strin += str(f)
                    add += 1
                if add == 2:
                    listF.append(strin)
                    add = 0
        else:
            for f in line['files']:
                if isinstance(f, dict):
                    for k ,v in f.items():
                        dictKey = v  
                        strin = k + ' (' + str(v) + ') '
                        add += 1
                else:
                    strin += str(f)
                    dictValue = f
                    add += 1
                if add == 2:
                    val = strin
                    if isinstance(dictKey, str):
                        char1 = '('
                        char2 = ')'
                        dictKey = k[k.find(char1)+1 : k.find(char2)]
                    dictL =( int(dictKey) , val )
                    newL.append(dictL)
                    newL = sorted(newL, key=lambda key: key[0]) 
                    add = 0
        for l in newL:
            k , v = l
            listF.append(v)                             
    listOrder = []
    listOrder.append('A-Z')
    listOrder.append('Occurance')
    return render_template('reprint.html',
                           title='Analysis',
                           n=fileName,
                           fileList=listF,
                           prev =listOrder)



def allowed_file(filename):
    """This function checking allowed file extensions"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    #app.run(debug=True)
	app.run(host='0.0.0.0',debug=True)
