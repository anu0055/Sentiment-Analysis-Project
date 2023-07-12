# EXAMPLE WEBSITE moneycontrol.com with the company as reliance 


import pandas as pd
from bs4 import BeautifulSoup
import csv 
import requests
import json
import re
import os

def get_blog_url(soup):
    div  =soup.find_all('div', attrs={'class':'FL PR20'})
    url_list =[]
    for title in div:
        href = title.find('a')['href']
        url_list.append("https://www.moneycontrol.com/"+href)
    return url_list

def get_blog_content(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    all_scripts = soup.find_all('script', attrs={'type':'application/ld+json'})
    raw_article_str= all_scripts[2].get_text().replace('\r\n',' ')
    parts = re.split(r"""("[^"]*"|'[^']*')""", raw_article_str)
    parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
    article_str= "".join(parts)
    article_str = article_str[1:]
    article_str = article_str[:-1]
    article_dict = json.loads(article_str)
    all_tags = soup.find_all('div', attrs={'class':'tags_first_line'})
    list_all_tags = []
    for i in all_tags:
        list_all_tags.append(i.get_text())
    tags= list_all_tags[0].replace('TAGS:', '')
    tags= tags.replace('\n', '')
    tags =tags.split('#')
    tags = tags[1:]
    tags = ','.join([str(elem).strip() for elem in tags])
    article_dict['tags']= tags
    return article_dict

def get_page_no(url, sc_id, page_no, next, year):
    request= requests.get(url)
    soup= BeautifulSoup(request.text, 'html.parser')
    
    all_page_no= soup.find_all('div', attrs={'class': 'pages MR10 MT15'})
    page_list=[i.text for i in all_page_no[0].find_all('a')]

    if any(map(str.isdigit, page_list[-1])):
        return int(page_list[-1]), next
    else:
        next = next+1
        page_no= int(page_list[-2])
        url = "https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id="+sc_id+"&scat=&pageno="+str(page_no)+"&next="+str(next)+"&durationType=Y&Year="+str(year)+"&duration=1&news_type="
        return get_page_no(url, sc_id, page_no, next, year)
    
def save_company_data(url_ = "https://www.moneycontrol.com/stocks/company_info/stock_news.php?", sc_id=[], page_no=1, next=0, years=[]):
    for company in sc_id:
        df= pd.DataFrame(columns=['company', 'datePublished', 'author', 'headline', 'description', 'articleBody', 'tags', 'url'])
        body=[]
        for year in years:
            print('year: ', year)
            print('page_no: ', page_no)
            print('next: ', next)
            
            url= url_ + "sc_id="+company+"&scat=&pageno="+str(page_no)+"&next="+str(next)+"&durationType=Y&Year="+str(year)+"&duration=1&news_type="
            print('url: ', url)
            
            max_page_no, max_next = get_page_no(url, company, page_no, next, year)
            max_next = max_next + 1
            
            for i in range(max_next):
                for j in range((i*10)+1, (i*10)+11):
                    if j<=max_page_no:
                        url_list =[]
                        url= url_ + "sc_id="+company+"&scat=&pageno="+str(j)+"&next="+str(i)+"&durationType=Y&Year="+str(year)+"&duration=1&news_type="
                        request = requests.get(url)
                        soup = BeautifulSoup(request.text, 'html.parser')
                        url_list = get_blog_url(soup)

                        for url in url_list:
                            try:
                                
                                article_dict = get_blog_content(url)
                                print(company)
                                print(article_dict['datePublished'])
                                print(article_dict['author'])
                                print(article_dict['headline'])
                                print(article_dict['description'])
                                print(article_dict['articleBody'])
                                print(article_dict['tags'])
                                print(article_dict['url'])
                                print('-------------------------------------')
                                #Storing process (storing the data into csv format)
                                article_lst = [[company,
                                                article_dict['datePublished'],
                                                article_dict['author'],
                                                article_dict['headline'],
                                                article_dict['description'],
                                                article_dict['articleBody'],
                                                article_dict['tags'],
                                                url]]
                                body.append(article_lst[0][5])
                                
                                df = df.append(pd.DataFrame(article_lst, columns=['company', 'datePublished', 'author', 'headline', 'description', 'articleBody','tags','url']), ignore_index= True)
                            except:
                                article_lst = [[company, 'error', 'error', 'error', 'error', 'error', 'error', url]]
                                df = df.append(pd.DataFrame(article_lst, columns=['company', 'datePublished', 'author', 'headline', 'description', 'articleBody', 'tags', 'url']), ignore_index= True)
                                
                                continue
                        else:
                            break
        if (sc_id=='HDF01'):
            df.to_csv('file1.csv', index=False)
        else:
            df.to_csv('file2.csv', index=False)                
        file = open('C:\\Users\\ANUBHAV UTKARSH\\OneDrive\\Desktop\\Sentiment Analysis Project\\file.txt','w', encoding='utf-8')
        for item in body:
            file.write(item+"\n") 
       
def main1():        
    print("\n--MONEY CONTROL NEWS--\n")
    
    for i in range(2):
        scid=[]
        y=[]
        a= input("Enter the sc_id for the company you want to get the data from the website: \n") 
        b= input("Enter the year from which you want the data from: \n")    
        scid.append(a)
        y.append(b)
        save_company_data(sc_id= scid, years=y)

    
main1()