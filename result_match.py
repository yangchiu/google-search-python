from selenium import webdriver
from bs4 import BeautifulSoup
import re
from google_search import GoogleSearch 

class ResultMatch(object):
    
    def __init__(self):
        self.driver = webdriver.PhantomJS('./phantomjs')
        self.extend_range = 16 * 5
        
    def is_chinese(self, ch):
        if ord(ch) >= 0x4e00 and ord(ch) <= 0x9fff:
            return True
        
    def strip(self, text):
        new_start = 0
        new_end = len(text)
        for index, ch in enumerate(text):
            if self.is_chinese(ch):
                break
            elif ch == ' ':
                new_start = index + 1
                break
            else:
                new_start = index + 1
        for index, ch in reversed(list(enumerate(text))):
            if self.is_chinese(ch):
                break
            elif ch == ' ':
                new_end = index
                break
            else:
                new_end = index

        return text[new_start:new_end]
        
    def visible(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        return True
        
    def match(self, url, sentence):
        print(url)
        # visit the page
        self.driver.get(url)
        # after page loaded, get its source
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        data = soup.findAll(text=True)
        # filter out unrelated content
        result = filter(self.visible, data)
        # get full article
        text = ' '.join(result)
        text_len = len(text)
        sent_len = len(sentence)
        
        # locate the position of the sentence in the full article
        index = text.find(sentence)
        # extend the sentence
        if index != -1:
            start_index = index - self.extend_range if index - self.extend_range >= 0 else 0
            end_index = index + sent_len
            end_index = end_index + self.extend_range if end_index + self.extend_range < text_len else text_len - 1
            # deal with tokenization
            print(f'before strip: {text[start_index:end_index]}')
            return self.strip(text[start_index:end_index])
        # if cannot find the sentence in the article, just return the orig sentence
        else:
            return sentence

if __name__ == '__main__':
    #query = 'deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 dif- ferent'
    #query = '各國迫切需要達成巴黎協定目標，以控制全球暖化在高於工業化前水平2°C以內。'
    query = 'we restricted our docking study to the 76 out of 104 cases where the protein binds to a single molecule of dsDNA'
    #query = 'and hidden unit j are on together when the feature detectors are being driven by images from the training set and'
    #query = 'To achieve its impressive performance in tasks such as speech perception or object recognition, the brain extracts multiple levels of representation from the sensory input'
    #query = 'a new learning algorithm that alleviates the problem of the potential convergence to a steady-state, named Active Hebbian Learning (AHL) is presented, validated and implemented'
    #query = 'In the past several years, a number of different language modeling improvements over simple trigram models have been found,'
    
    # query a string in google
    searcher = GoogleSearch()
    results = searcher.search(query)
    print(results)
    
    # get a query result summary provided by google
    # and
    # get the url of this query result webpage
    # then
    # get the full article of this webpage
    # then
    # search for the query result summary in the full article
    # finally
    # get a longer summary
    result_match = ResultMatch()
    entry = {}
    for result in results:
        if result['mime'] == 'web':
            entry = result
            break
    print(f'search for: {entry["best_matched"]}')
    res = result_match.match(entry['href'], entry['best_matched'])
    print(f'extended result: {res}')
    
    
    filename = "dynamic_result.html"
    file = open(filename, 'w')
    file.write(res)
    file.close()

