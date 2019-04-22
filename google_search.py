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
        
        self.rep = {'<b>': '',
                    '</b>': '',
                    '<br/>': '',
                    '<span class="st">': '',
                    '</span>': '',
                    '<em>': '',
                    '</em>': '',
                    '\n': '',
                    '\xa0': ''}
        self.rep = dict((re.escape(k), v) for k, v in self.rep.items())
        self.rep_pattern = re.compile("|".join(self.rep.keys()))
        
    def parse_page(self, page):
        page = BeautifulSoup(page, 'lxml')
        
        filename = "sample4.html"
        myfile = open(filename, 'w')
        myfile.write(str(page))
        myfile.close()
        
        results = []
        
        try:
            # collect all search result entries
            divs = page.find_all('div', 'g')
            #print(divs)
            for div in divs:
                # init object
                result = {}
                
                # get href
                pattern = re.compile('http.*(?=\&sa\=U)|http.*')
                try:
                    result_url = pattern.findall(div.find('a')['href'])
                    result['href'] = urllib.request.unquote(result_url[0])
                except:
                    continue
                    
                # get title and summary
                st = div.find('span', {'class': 'st'})
                if not st:
                    continue
                else:
                    result['title'] = div.find('h3').text
                if not st.text:
                    continue
                else:
                    result['summary'] = st.text
                    
                # get mime type
                mime = div.find('span', {'class': 'mime'})
                if not mime:
                    result['mime'] = 'web'
                else:
                    result['mime'] = mime.text
                
                # collect results
                results.append(result)
                
                # extract the best matched sentence in the summary
                summary_list = re.split('\s-\s|\.{3,}', str(st))
                max_count = 0
                max_count_index = 0
                for index, sub in enumerate(summary_list):
                    count = sub.count('<b>')
                    if count > max_count:
                        max_count = count
                        max_count_index = index
                if max_count != 0:
                    best = self.rep_pattern.sub(lambda m: self.rep[re.escape(m.group(0))],
                                                summary_list[max_count_index])
                else:
                    best = ''
                result['best_matched'] = best.strip()
                
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
    query = 'number of copies that all have the same weights but have progressively more negative biases. The learning and inference rules for these “Stepped'
    searcher = GoogleSearch()
    results = searcher.search(query)
    print(results)
        
        