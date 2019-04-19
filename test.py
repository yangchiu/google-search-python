from selenium import webdriver
from bs4 import BeautifulSoup
import re
import urllib.request
import zlib

opener = urllib.request.build_opener()
header = [('Accept-Language', 'en-US,en;q=0.8'),
          ('Accept-Encoding', 'gzip'),
          ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
          ('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; it; rv:1.9.0.8) Gecko/2009033100 Ubuntu/9.04 (jaunty) Firefox/3.0.8'),
          ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
          ('Connection', 'keep-alive')
         ]
opener.addheaders = header

engineUrl = 'https://www.google.com/search?q='
query = 'We generated two sets of decoy poses-one treating DNA as the static molecule with a translating/rotating protein referred to as the sDNA decoy set'
query = query.split()
encodeQuery = engineUrl + urllib.request.quote(' '.join(query))

print(encodeQuery)

response = None
currentRetryTimes = 0
retryTimes = 10
timeout = 0

while (response is None) and currentRetryTimes<retryTimes:
    try:
        if timeout:
            response = opener.open(encodeQuery,timeout=timeout)
        else:
            response = opener.open(encodeQuery)
        print('reading response')
    except urllib.request.HTTPError as e: 
        raise self.handleHTTPError(e)
    except urllib.request.URLError as e:
        currentRetryTimes += 1
        print('retry {times}!'.format(times=currentRetryTimes))
        if currentRetryTimes == retryTimes:
            raise e

unZipResult = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)

def parsePage(page):
    page = BeautifulSoup(page, 'lxml')
    #print("+++++++++++++++++++++++++++++++++++++")
    #print(page)
    #print("+++++++++++++++++++++++++++++++++++++")
    resultlist = []
    try:
        pattern = re.compile('http.*(?=\&sa\=U)|http.*')
        divs = page.find_all('div', 'g')
        #print(divs)
        for div in divs:
            result = {}
            st = div.find('span', {'class': 'st'})
            if st:
                targetUrl = pattern.findall(div.find('a')['href'])
                print(targetUrl)
                if not targetUrl:
                    continue
                result['href'] = urllib.request.unquote(targetUrl[0])
                print("href")
                print(result['href'])
                
                result['title'] = div.find('h3').text
                print("title")
                print(result['title'])
                result['content'] = st.text
                resultlist.append(result)
        return resultlist
    except Exception as error:
        fileName = time.time()
        with open('{0}.html'.format(fileName), 'w') as htm:
            self.logger.error('{0} when parse {1}.html'.format(str(error), fileName), exc_info=True)
            htm.write(page.__str__())
        raise
    
results = parsePage(unZipResult)

print(results)
#opener.open(encodeQuery)
 
driver = webdriver.PhantomJS('./phantomjs')
driver.get('https://pubs.acs.org/doi/full/10.1021/acs.jctc.6b00688?src=recsys')

soup = BeautifulSoup(driver.page_source, 'lxml')
data = soup.findAll(text=True)
 
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True
 
result = filter(visible, data)

text = ''.join(result)

#print("+++++++++++++++++++++++++++++++++++++")
#filename = "sample2.html"
 
# Open the file with writing permission
#myfile = open(filename, 'w')
 
# Write a line to the file
#myfile.write(str(unZipResult))
 
# Close the file
#myfile.close()
 
#print(text)
