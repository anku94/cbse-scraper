import requests, shutil, re, sys, pytesseract
import time as Time
from multiprocessing.dummy import Pool, TimeoutError
from PIL import Image

validSessions = {}

GENERIC_HEADERS = {
        'Pragma': 'no-cache',
        'Origin': 'http://schoolcoderesults.nic.in',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8,ms;q=0.6',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Referer': 'http://schoolcoderesults.nic.in/cbserslt16/result.php',
        'Connection': 'keep-alive'
        }

CAPTCHA_HEADERS = {
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,ms;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Referer': 'http://schoolcoderesults.nic.in/cbserslt16/result.php',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
        }

def copyDic(d):
    newDic = {}
    for i in d:
        newDic[i] = d[i]
    return newDic

def generateSession():
    URL = 'http://schoolcoderesults.nic.in/cbserslt16/result.php'
    r = requests.post(URL, headers=GENERIC_HEADERS)
    return r.cookies['PHPSESSID']

def getCaptcha(sessionID):
    URL = 'http://schoolcoderesults.nic.in/cbserslt16/randomImage.php'
    headers = copyDic(CAPTCHA_HEADERS)
    headers['Cookie'] = 'PHPSESSID=' + sessionID
    #print headers['Cookie']
    r = requests.get(URL, headers=headers, stream=True)
    with open('captcha/' + sessionID + '.jpeg', 'wb') as out:
        shutil.copyfileobj(r.raw, out)
    del r

def decodeCaptcha(sessionID):
    #print sessionID
    fileName = "captcha/" + sessionID + ".jpeg"
    imageObject = Image.open(fileName)

    return pytesseract.image_to_string(imageObject).upper()

# data.sessionID and data.captcha
def makeRequest(data):
    print "Data: ", data
    headers = copyDic(GENERIC_HEADERS)
    headers['Cookie'] = 'PHPSESSID=' + data['sessionID']

    payload = {
            'selClass': '12',
            'txtAffl': data['txtAffl'],
            'txtCode': data['txtCode'],
            'txtEmail': 'recruiter.anastasia@gmail.com',
            'txtNumber': data['captcha']
            }

    r = requests.post('http://schoolcoderesults.nic.in/cbserslt16/cbse_mail.php', headers=headers, data=payload)
    if len(re.findall('All the best!!!', r.text)) > 0 :
        return (True, "Success", data['txtAffl'])
    elif len(re.findall('Affiliation Code is not valid', r.text)) > 0:
        return (True, "Invalid Affiliation", data['txtAffl'])
    elif len(re.findall('No result could be found for', r.text)) > 0 :
        return (True, "Result Not Found", data['txtAffl'])
    elif len(re.findall('You have provided the Affiliation Code : ', r.text )) > 0:
        return (True, "Incorrect Code", data['txtAffl'])
    else:
        if(len(re.findall('Image text entered', r.text)) == 0):
            print r.text
        return (False, r.text, data['txtAffl'])

def getSession():
    sessions = validSessions.keys()
    if len(sessions) > 0:
        return (sessions[0], validSessions[sessions[0]])
    else:
        session = generateSession()
        print 'Creating new session: ', session
        getCaptcha(session)
        captcha = decodeCaptcha(session)
        validSessions[session] = captcha
        return (session, captcha)

def invalidateSession(sessionID):
    if sessionID in validSessions:
        del validSessions[sessionID]
        return True
    else:
        return False

def poolWorker(data):
    data = data.strip().split(',')
    print 'Processing: ', data

    reqArgs = {}
    reqArgs['txtAffl'] = data[0].strip()
    reqArgs['txtCode'] = data[1].strip()

    session = getSession()
    reqArgs['sessionID'] = session[0]
    reqArgs['captcha'] = session[1]

    
    while True:
        try:
            print "Session array: ", len(validSessions.keys())
            res = makeRequest(reqArgs)
            if res[0]:
                return res
            else:
                invalidateSession(session[0])
                session = getSession()
                reqArgs['sessionID'] = session[0]
                reqArgs['captcha'] = session[1]
        except Exception as e:
            print e
            Time.sleep(5)

def runPool(fname):
    pool = Pool(16)
    data = open(fname)
    for i in pool.imap(poolWorker, data):
       print i
    #for i in data:
    #    print poolWorker(i)
    return

if __name__ == '__main__':
    runPool(sys.argv[1])
