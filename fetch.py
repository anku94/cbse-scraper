import requests, shutil, re, sys
from multiprocessing import Pool, TimeoutError

validSessions = {'7fc493b6e7f56b73043793455a814a3b': 'TR31S'}

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
    print headers['Cookie']
    r = requests.get(URL, headers=headers, stream=True)
    with open('captcha/' + sessionID + '.png', 'wb') as out:
        shutil.copyfileobj(r.raw, out)
    del r

def decodeCaptcha(sessionID):
    print sessionID
    return 'ABCDEF'

# data.sessionID and data.captcha
def makeRequest(data):
    print "Data: ", data
    headers = copyDic(GENERIC_HEADERS)
    headers['Cookie'] = 'PHPSESSID=' + data['sessionID']

    payload = {
            'selClass': '12',
            'txtAffl': data['txtAffl'],
            'txtCode': data['txtCode'],
            'txtEmail': '1recruiter.anastasia@gmail.com',
            'txtNumber': data['captcha']
            }

    r = requests.post('http://schoolcoderesults.nic.in/cbserslt16/cbse_mail.php', headers=headers, data=payload)
    if len(re.findall('All the best!!!', r.text)) > 0:
        return (True, '')
    else:
        return (False, r.text)

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
        return false

def poolWorker(data):
    data = data.strip().split(',')
    print 'Processing: ', data

    reqArgs = {}
    reqArgs['txtAffl'] = data[0].strip()
    reqArgs['txtCode'] = data[1].strip()

    session = getSession()
    reqArgs['sessionID'] = session[0]
    reqArgs['captcha'] = session[1]

    res = makeRequest(reqArgs)
    if res[0]:
        return res
    else:
        invalidateSession(session[0])
        session = getSession()
        reqArgs['sessionID'] = session[0]
        reqArgs['captcha'] = session[1]
        res = makeRequest(reqArgs)
        return res

def runPool(fname):
    pool = Pool(1)
    data = open(fname)
    for i in pool.imap_unordered(poolWorker, data):
        print i
    # for i in data:
        # print poolWorker(i)
    return

if __name__ == '__main__':
    runPool(sys.argv[1])
