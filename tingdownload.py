#!/usr/bin/env python2
# coding=utf-8

# desc: download mp3 from ting.baidu.com
# author: vonnyfly <lifeng1519@gmail.com>
# date: 2013-03-13

import sys
import os
import urllib
import urllib2
import logging
import re
import argparse
import json
import cookielib
import time
#cookie
cj = cookielib.CookieJar();
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj));
urllib2.install_opener(opener);

#log
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

reload(sys)
sys.setdefaultencoding(sys.getfilesystemencoding())  # for cross-platform

class DownloadError(Exception):
    """a user defined exception for download error"""
    pass

class NotFoundError(Exception):
    """a user defined exception for not found"""
    pass

class TooMoreFoundError(Exception):
    """a user defined exception for too more result found"""
    pass

class FileExistError(Exception):
    """a user defined exception for file exist"""
    pass

class SysDefenceError(Exception):
    """system find a robot"""
    pass

class TingDownloadInfo(object):
    """result info"""
    count = 0
    header = '== %(message)s (%(count)d) ==\n'
    logger_text = ''
    message = ''

    def log(self, text):
        self.logger_text += text + '\n'
        self.count += 1

    def get_result(self):
        if self.count == 0:
            return ''
        result = self.header % {'message': self.message, 'count': self.count}
        for line in self.logger_text:
            result += line
        return result + '\n'

class TingDownloadInfo200(TingDownloadInfo):
    def __init__(self):
        super(TingDownloadInfo200, self).__init__()
        self.message = 'Download success'

class TingDownloadInfo304(TingDownloadInfo):
    def __init__(self):
        super(TingDownloadInfo304, self).__init__()
        self.message = 'Download failed for file exists'

class TingDownloadInfo400(TingDownloadInfo):
    def __init__(self):
        super(TingDownloadInfo400, self).__init__()
        self.message = 'Download failed for too many result'

class TingDownloadInfo404(TingDownloadInfo):
    def __init__(self):
        super(TingDownloadInfo404, self).__init__()
        self.message = 'Download failed for not fount'

class TingDownloadInfo500(TingDownloadInfo):
    def __init__(self):
        super(TingDownloadInfo500, self).__init__()
        self.message = 'Download failed for network error'

class MusicInfo(object):
    """ting music"""

    def __init__(self, id, song_name, artist_name):
        self.id = id
        self.song_name = song_name
        self.artist_name = artist_name

    def __repr__(self):
        return u'%s %s - %s' % (self.id, self.artist_name, self.song_name)

class TingDownload(object):
    """a download helper for ting.baidu.com"""

    SEARCH_URL = u'http://openapi.baidu.com/public/2.0/mp3/info/suggestion?' \
                'format=json&word=%(word)s&callback=window.baidu.sug'
    DOWNLOAD_URL = u'http://ting.baidu.com/song/%s/download'
#    TARGET_URL = u'http://ting.baidu.com%s'

    MUSICS_DIR = os.path.abspath('./musics')

    def __init__(self, name,rate):
        self.name = name
        if not os.path.exists(self.MUSICS_DIR):
            os.mkdir(self.MUSICS_DIR)
        self.rate = rate
        
    def download(self):
        try:
            self.music_info = self.search()
        except urllib2.URLError, e:
            logger.info('X Error, please check network.')
            raise DownloadError(e)
        except NotFoundError, e:
            logger.info(e)
            raise e
        except TooMoreFoundError, e:
            logger.info(e)
            raise e
        except SysDefenceError,e:
            logger.info(e)
            raise e
        try:
            if os.path.exists(self.path_name):
                raise FileExistError('# Info, file: "%s" exists.' \
                                     % self.path_name)
            self.target_url = self.fetchMusic()
            self.write_file()
            logger.info('V Info, download complete.')
        except urllib2.URLError, e:
            logger.info(e)
            raise DownloadError(e)
        except FileExistError, e:
            logger.info(e)


    def search(self):
        word = urllib2.quote(self.name.encode('utf-8'))
        url = self.SEARCH_URL % {'word': word}
        handler = urllib2.urlopen(url)
        json_text = handler.read()
        json_result = json.loads(json_text.strip()[17:-2])
        if len(json_result['song']) < 1:
            raise NotFoundError(u"X Error, can't find song: %s." % self.name)

        music = MusicInfo(json_result['song'][0]['songid'],
                          json_result['song'][0]['songname'],
                          json_result['song'][0]['artistname'])
        if len(json_result['song']) > 1:
            logger.info('# Info, auto match first one song: %s - %s.'
                        % (music.artist_name, music.song_name))
        self.path_name = os.path.join(
            self.MUSICS_DIR,
            music.artist_name + '-' \
            + music.song_name + '.mp3'
            )
        return music

    def fetchMusic(self):
        """get the link of music"""
#        print 'http://zhangmenshiting.baidu.com/data2/music/34598588/339095011363089661192.mp3?xcode=a44a2002829aedafd87fbce7546e1210'
        page = urllib2.urlopen(self.DOWNLOAD_URL % self.music_info.id).read()
#        for index, cookie in enumerate(cj):
#            print '[',index, ']',cookie;
#        f = open("xxx.html",'w')
#        f.write(page)
#        f.close()
#        p = re.findall('<input  style="display:none;"  downlink="(.*?)"', page, re.DOTALL)
       
#               if(self.rate == 'h'):
#            downloadUrl = re.findall('\{"rate":320,"link":"(.*?)"\}', page, re.DOTALL)
#            if (len(downloadUrl) < 1):
#                self.rate = 'm'
#                downloadUrl = re.findall('\{"rate":192,"link":"(.*?)"\}', page, re.DOTALL)
#                if (len(downloadUrl) < 1):
#                    downloadUrl = re.findall('<a href="/data/music/file\?link=(.*?)"', page, re.DOTALL)
        if(self.rate == 'h'):
            downloadUrl = re.findall('\{"rate":320,"link":"(.*?)"\}', page, re.DOTALL)
        if(len(downloadUrl) <1):
            downloadUrl = re.findall('\{"rate":192,"link":"(.*?)"\}', page, re.DOTALL)
        if(len(downloadUrl) <1):
            downloadUrl = re.findall('<a href="/data/music/file\?link=(.*?)"', page, re.DOTALL)
        if(len(downloadUrl) <1):
            raise SysDefenceError(u"System found I am a robot~~~~")
        downloadUrl = downloadUrl[0].replace('\\','')
        return downloadUrl

    def write_file(self):
        """save music to disk"""
#        print self.target_url, self.path_name
        urllib.urlretrieve(self.target_url, self.path_name)

def zh2unicode(text):
    """
    Auto converter encodings to unicode
    It will test utf8, gbk, big5, jp, kr to converter"""
    for encoding in ('utf-8', 'gbk', 'big5', 'jp', 'euc_kr', 'utf16', 'utf32'):
        try:
            return text.decode(encoding)
        except:
            pass
    return text

def mdcode(str):
    for c in ('utf-8', 'gbk', 'gb2312'):
        try:
            return str.decode(c).encode('utf-8')
        except:
            pass
    return 'unknown'


#------------------------------------------------------------------------------
# check all cookies in cookiesDict is exist in cookieJar or not
def checkAllCookiesExist(cookieNameList, cookieJar) :
    cookiesDict = {};
    for eachCookieName in cookieNameList :
        cookiesDict[eachCookieName] = False;
     
    allCookieFound = True;
    for cookie in cookieJar :
        if(cookie.name in cookiesDict) :
            cookiesDict[cookie.name] = True;
     
    for eachCookie in cookiesDict.keys() :
        if(not cookiesDict[eachCookie]) :
            allCookieFound = False;
            break;
 
    return allCookieFound;
 
#------------------------------------------------------------------------------
# just for print delimiter
def printDelimiter():
    print '-'*80;
 
#------------------------------------------------------------------------------
# main function to emulate login baidu
def emulateLoginBaidu(username,password):
    printDelimiter();
 
#    # parse input parameters
#    parser = optparse.OptionParser();
#    parser.add_option("-u","--username",action="store",type="string",default='',dest="username",help="Your Baidu Username");
#    parser.add_option("-p","--password",action="store",type="string",default='',dest="password",help="Your Baidu password");
#    (options, args) = parser.parse_args();
#    # export all options variables, then later variables can be used
#    for i in dir(options):
##        print i + " = options." + i
#        exec(i + " = options." + i);
 
    print "[preparation] using cookieJar & HTTPCookieProcessor to automatically handle cookies";
    printDelimiter();
    print "[step1] to get cookie BAIDUID";
    baiduMainUrl = "http://www.baidu.com/";
    resp = urllib2.urlopen(baiduMainUrl);
    #respInfo = resp.info();
    #print "respInfo=",respInfo;
#    for index, cookie in enumerate(cj):
#        print '[',index, ']',cookie;
 
    printDelimiter();
    print "[step2] to get token value";
    getapiUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true";
    getapiResp = urllib2.urlopen(getapiUrl);
    #print "getapiResp=",getapiResp;
    getapiRespHtml = getapiResp.read();
    #print "getapiRespHtml=",getapiRespHtml;
    #bdPass.api.params.login_token='5ab690978812b0e7fbbe1bfc267b90b3';
    foundTokenVal = re.search("bdPass\.api\.params\.login_token='(?P<tokenVal>\w+)';", getapiRespHtml);
    if(foundTokenVal):
        tokenVal = foundTokenVal.group("tokenVal");
        print "tokenVal=",tokenVal;
 
        printDelimiter();
        print "[step3] emulate login baidu";
#        staticpage = "http://www.baidu.com/cache/user/html/jump.html";
        staticpage = 'http://music.baidu.com/static/html/pass_jump.html'
        baiduMainLoginUrl = "https://passport.baidu.com/v2/api/?login";
        postDict = {
            #'ppui_logintime': "",
            'charset'       : "utf-8",
            #'codestring'    : "",
            'token'         : tokenVal, #de3dbf1e8596642fa2ddf2921cd6257f
            'isPhone'       : "false",
            'index'         : "0",
            #'u'             : "",
            #'safeflg'       : "0",
            'staticpage'    : staticpage, #http%3A%2F%2Fwww.baidu.com%2Fcache%2Fuser%2Fhtml%2Fjump.html
            'loginType'     : "1",
            'tpl'           : "mn",
            'callback'      : "parent.bdPass.api.login._postCallback",
            'username'      : username,
            'password'      : password,
            #'verifycode'    : "",
            'mem_pass'      : "on",
        };
        postData = urllib.urlencode(postDict);
        # here will automatically encode values of parameters
        # such as:
        # encode http://www.baidu.com/cache/user/html/jump.html into http%3A%2F%2Fwww.baidu.com%2Fcache%2Fuser%2Fhtml%2Fjump.html
        #print "postData=",postData;
        req = urllib2.Request(baiduMainLoginUrl, postData);
        # in most case, for do POST request, the content-type, is application/x-www-form-urlencoded
        req.add_header('Content-Type', "application/x-www-form-urlencoded");
        resp = urllib2.urlopen(req);
#        for index, cookie in enumerate(cj):
#            print '[',index, ']',cookie;
        cookiesToCheck = ['BDUSS', 'PTOKEN', 'STOKEN', 'SAVEUSERID'];
        loginBaiduOK = checkAllCookiesExist(cookiesToCheck, cj);
        if(loginBaiduOK):
            print "+++ Emulate login baidu is OK, ^_^";
        else:
            print "--- Failed to emulate login baidu !"
    else:
        print "Fail to extract token value from html=",getapiRespHtml;

def main():
    # prepare args
    parser = argparse.ArgumentParser(
        description='A script to download music from music.baidu.com.'
    )

    parser.add_argument('keywords', metavar='Keyword', type=str, nargs='*',)
    parser.add_argument('-i', '--input', help='a list file to input musics',
                        type=argparse.FileType('r'))
    parser.add_argument("-u","--username",action="store",type=str,
                      default='',help="Your Baidu Username");
    parser.add_argument("-p","--password",action="store",type=str,
                      default='',help="Your Baidu password");
    parser.add_argument("-q","--rate",action="store",type=str,
                      default='h',nargs='?',help="Music rate and quality,l:low,128,m:middle,192,h:high,320");
                                     
    args = parser.parse_args()

    
    username = args.username
    password = args.password
    rate = args.rate
    keywords = args.keywords
    if args.input != None:
        keywords = zh2unicode(args.input.read()).splitlines()

    if len(keywords) == 0:
        parser.print_help()
        return

    # prepare loggers
    info200 = TingDownloadInfo200()
    info304 = TingDownloadInfo304()
    info400 = TingDownloadInfo400()
    info404 = TingDownloadInfo404()
    info500 = TingDownloadInfo500()
    

    emulateLoginBaidu(username,password)
    for name in keywords:
        try:
            logger.info('> Start search %s...' \
                     % name.strip())
            tingDownload = TingDownload(re.sub(r'\s+', ' ', name.strip()),
                                        rate)
            tingDownload.download()
            info200.log(name)
        except NotFoundError, e:
            info404.log(name)
            continue
        except TooMoreFoundError, e:
            info400.log(name)
            continue
        except DownloadError, e:
            info500.log(name)
            os.remove(tingDownload.path_name)  # delte the error file
            continue
        except FileExistError, e:
            info304.log(name)
            continue
        except SysDefenceError,e:
            print "-----need wait a little time-----"
            time.sleep(60*10)
            continue
        except KeyboardInterrupt:
            os.remove(tingDownload.path_name)  # delte the error file
            break

    print_result(info200, info304, info400, info404, info500)

def print_result(info200, info304, *failed_loggers):
    sys.stdout.write('\n')
    sys.stdout.write(info200.get_result())
    sys.stdout.write(info304.get_result())
    for logger in failed_loggers:
        sys.stdout.write(logger.get_result())

if __name__ == '__main__':
    main()
