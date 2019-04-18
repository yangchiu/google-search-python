from bs4 import BeautifulSoup
import re
import urllib.request
import zlib
import time

class GoogleSearch(object):
    
    def __init__(self):
        self.opener = urllib.request.build_opener()
        
        header = [('Accept-Language', 'en-US,en;q=0.8'),
                  ('Accept-Encoding', 'gzip'),
                  ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                  ('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; it; rv:1.9.0.8) Gecko/2009033100 Ubuntu/9.04 (jaunty) Firefox/3.0.8'),
                  ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
                  ('Connection', 'keep-alive')
                 ]
        self.opener.addheaders = header

        self.engine_url = 'https://www.google.com/search?q='
        self.max_retry_times = 10
        
    def parse_page(self, page):
        page = BeautifulSoup(page, 'lxml')
        results = []
        
        pattern = re.compile('http.*(?=\&sa\=U)|http.*')
        
        try:
            divs = page.find_all('div', 'g')
            #print(divs)
            for div in divs:
                result = {}
                st = div.find('span', {'class': 'st'})
                if st:
                    result_url = pattern.findall(div.find('a')['href'])
                    if not result_url:
                        continue
                    result['href'] = urllib.request.unquote(result_url[0])
                    print(f'href = {result["href"]}')
                
                    result['title'] = div.find('h3').text
                    print(f'title = {result["title"]}')
                    
                    result['summary'] = st.text
                    results.append(result)
            return results
        except Exception as error:
            fileName = time.time()
            with open(f'{fileName}.html', 'w') as file:
                print(f'{error} when parsing {fileName}.html')
                file.write(str(page))
            raise
        
    def search(self, query_str):
        query_str = query_str.split()
        encoded_query = self.engine_url + urllib.request.quote(' '.join(query_str))
        #print(encoded_query)

        response = None
        current_retry_times = 0

        while response is None and current_retry_times < self.max_retry_times:
            try:
                response = self.opener.open(encoded_query)
                #print('reading response')
            except urllib.request.HTTPError as e: 
                raise self.handleHTTPError(e)
            except urllib.request.URLError as e:
                current_retry_times += 1
                print(f'retry {current_retry_times} times!')
            if current_retry_times == self.max_retry_times:
                raise e

        unzipped_result = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)
        results = self.parse_page(unzipped_result)
        return results
    
if __name__ == '__main__':
    query = 'We generated two sets of decoy poses-one treating DNA as the static molecule with a translating/rotating protein referred to as the sDNA decoy set'
    searcher = GoogleSearch()
    results = searcher.search(query)
    print(results)
        
        