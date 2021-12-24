#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 11:13:49 2021

@author: thomas hendry 2021
LitFinder program
www.tmhendry.com
"""

def title1():
    print("0: Setup (Please select this option first)")
    print("1: Google Search")
    print("2: Scopus Search")
    print("3: Google Scholar Search")
    print("4: ABDC Quality Check")
    print("5: Relevance Checker")
    print("6: Compile refer library")
    print("7: Open Search file")
    print("8: Exit")
    
    option1 = int(input("Option: "))
    
    if option1 == 1:
        googlesearch1()    
    elif option1 == 0:
        csvcreate()
    elif option1 == 2:
        scopus_search()
    elif option1 == 4:
        abdccheck()
    elif option1 == 5:
        relevance()
    elif option1 == 6:
        refer()
    elif option1 == 7:
        import os
        os.system("xdg-open df.csv")
        title1()
    elif option1 == 8:
        quit()
        
def csvcreate():
    
    config_proceed = str(input("Update your Google API key and Search engine ID (y/n)?: "))
    if config_proceed == 'y':    
    
        import configparser
        config = configparser.ConfigParser()
        print("To use the Googe search function you will need a Google Developer API key",
              "and a programmable search engine ID. Visit www.developers.google.com for information.")
        api_google = str(input("Enter your Google Developer API key: "))
        searchid = str(input("Enter your Google Search Engine ID: "))
        config['SETTINGS'] = {'API': api_google,
                              'SEARCHID': searchid}

        with open('config.ini', 'w') as configfile:
                config.write(configfile)
                           
    import csv
    
    proceed1 = str(input('Create a new df.csv to store your results (y/n)?: '))
    if proceed1 == 'y':
        with open('df.csv', 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['Program','Date','Query','Title','Author',
                                     'Year','Volume','Issue','Page',
                                     'Journal','URL','Snippet','Relevant'])
        print('Okay, a new csv file (df.csv) has been created!')
        title1()
    if proceed1 == 'n':
        title1()
    else:
        print("Sorry, that is not a valid option. Please type 'y' or 'n' (lowercase)")
        title1()
        
def googlesearch1():
    def googlesearch(QUERY,YEARS,FILETYPE,LOCATION,PAGE):
        import requests
        import pandas as pd
        import datetime
        pd.options.mode.chained_assignment = None  # default='warn'
    
        start = (PAGE - 1) * 10 + 1
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={QUERY}&start={start}&dateRestrict=y[{YEARS}]&fileType={FILETYPE}&gl={LOCATION}"
        data = requests.get(url).json()
        df = pd.read_csv("df.csv")
        df_google = []
        search_items = data.get("items")
    
        for i, search_item in enumerate(search_items, start=1):
            title = search_item.get("title")
            link = search_item.get("link")
            snippet = search_item.get("snippet")
            df_google.append(
                {
                    'Program': 'Google',
                    'Date': datetime.datetime.now(),
                    'Query': QUERY,
                    'Title': title,
                    'Snippet': snippet,
                    'URL': link
                    }
                )
        pd.DataFrame(df_google)
        df = df.append(df_google, ignore_index = True)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.to_csv('df.csv')
        print("Page",PAGE,"saved in df.csv.")
        CONT = str(input("Continue to next page (y/n)?: "))
    
        if CONT == 'y':
            PAGE = PAGE + 1
            googlesearch(QUERY,YEARS,FILETYPE,LOCATION,PAGE)
        
        elif CONT == 'n':
            print("Finished")
            print("")
            title1()
    
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    API_KEY = config['SETTINGS']['API']
    SEARCH_ENGINE_ID = config['SETTINGS']['SEARCHID']
    print("Search Google (not Google Scholar) for files according to a specified query.",
          "The csv file is updated with file information.")
    QUERY = str(input("Type your query: "))
    YEARS = int(input("How many years back would you like to search?: "))
    FILETYPE = str(input("What file type would you like (i.e. pdf, doc etc.)?: "))
    LOCATION = str(input("What location would you like to search from (i.e. au, us etc.)?: "))  
    PAGE = int(input("What page from the search?: "))
    googlesearch(QUERY,YEARS,FILETYPE,LOCATION,PAGE)
    
def scopus_search():
    from pybliometrics.scopus import ScopusSearch
    import pandas as pd
    import datetime
    
    print("Search Scopus for papers according to a specified query.",
          "The csv file is updated with file information.",
          "Refer to Scopus for field codes.")
    
    QUERY_SCOPUS = str(input("Type your query: "))
    
    s = ScopusSearch(QUERY_SCOPUS, subscriber=True)
    
    df_scopus = pd.DataFrame(pd.DataFrame(s.results))
    df_scopus['Program'] = 'Scopus'
    df_scopus['Date'] = datetime.datetime.now()
    df_scopus['Query'] = QUERY_SCOPUS
    df_scopus = df_scopus[['Program','Date','Query','title','author_names','coverDate',
             'volume','issueIdentifier','pageRange','publicationName',
             'description','doi']]
    df_scopus['doi'] = str('https://www.doi.org/')+df_scopus['doi'] 
    df_scopus.rename(columns = {'title':'Title','author_names':'Author','coverDate':'Year',
                         'volume':'Volume','issueIdentifier':'Issue','pageRange':'Page',
                         'publicationName':'Journal','description':'Snippet',
                         'doi':'URL'},inplace = True)
    df_scopus['Year'] = df_scopus['Year'].astype(str).str[:4]
    
    print('The search found',len(df_scopus.Year),'results. The df.csv file has been updated.')
    
    df = pd.read_csv("df.csv")
    df = df.append(df_scopus, ignore_index = True)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.to_csv('df.csv')
    title1()

def abdcreduce():
    import pandas as pd
    journals = pd.read_csv('journals.csv')
    journals = journals[['Title', 'Rating']]
    journals.rename(columns = {'Title':'Journal'},inplace = True)
    results = pd.read_csv('df.csv')
    
    if 'Rating' in results.columns:
        del results['Rating']
    
    results2 = pd.merge(results, journals, on = ['Journal'], how = 'outer')
    df = results2[['Program','Date','Query','Title','Author','Year','Volume',
                   'Issue','Page','Journal','URL','Snippet','Rating','Relevant'
                   ]]
    df.dropna(subset = ['Program'], inplace = True)
    df = df.sort_values(by=['Rating'])   
    df.Rating = df.Rating.fillna('No rating')
    df.to_csv("df.csv")
    print("The csv file has been updated with ABDC ratings.")
    title1()

def abdccheck():
    import pandas as pd
    import numpy as np
    journals = pd.read_csv("journals.csv")
    searches = pd.read_csv("df.csv")
    print("Your searches have resulted in", len(searches), "papers.")
    searches["Rated"] = np.where(searches.Journal.isin(journals.Title), True, False)
    searches2 = searches[searches.Rated == True]
    print(len(searches2), "papers are rated by ABDC.")
    goahead = str(input("Proceed to update csv (y/n)?: "))
    
    if goahead == 'y':
        abdcreduce()
    else:
        title1()

def relevance():
    import pandas as pd
    pd.options.mode.chained_assignment = None  # default='warn'
    df = pd.read_csv('df.csv')
    
    dupes = str(input("Before sorting the relevant papers, do you want to delete any duplicates (y/n)?: "))
    
    if dupes == 'y':
        x = len(df.Program)
        df = df.drop_duplicates(subset=['Title', 'URL'])
        print(x-len(df.Program),"duplicates were removed.")
    
    for i in df.index:
        if df.Relevant[i] == 'True':
            df.Relevant[i] = df.Relevant[i]
        elif df.Relevant[i] == 'False':
            df.Relevant[i] = df.Relevant[i]
        else:
            print("")
            print('Title:',df.Title[i])
            print("")
            print('Snippet:',df.Snippet[i])
            print("")
            print('Rating:',df.Rating[i])
            print("")
            rel = str(input('Is this paper relevant (k=keep, l=leave out, e=exit)?: '))
    
            if rel == 'e':
                df = df[['Program','Date','Query','Title','Author','Year','Volume',
                         'Issue','Page','Journal','URL','Snippet','Rating',
                         'Relevant']]
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                df.Relevant = df.Relevant.fillna('Not checked')
                df.to_csv('df.csv')
                print("The csv file has been updated.")
                title1()
        
            elif rel == 'k':
                df.Relevant[i] = True
        
            elif rel == 'l':
                df.Relevant[i] = False

def refer():
    import pandas as pd
    import os
    df = pd.read_csv("df.csv")
    df.Year.fillna(1000,inplace=True)
    df.fillna('',inplace=True)
    
    print("This program will replace any existing refer bibliography file.",
          "The file may have incomplete data (especially from Google).")
    
    proc = str(input("Proceed (y/n)?: "))
    
    if os.path.exists('bib.txt') == True:
        os.remove('bib.txt')
        
    if proc == 'y': 
        
        limitr = str(input("Limit to relevant papers (y/n)?: "))
        if limitr == 'y':
            df = df[df.Relevant == 'True']
            
        for i in df.index:
            x = df.Author.str.split(';', expand=False)
            for p in x[i]:
                print('%A',p,file=open("bib.txt", "a"))
            print('%T',df.Title[i],file=open("bib.txt", "a"))
            print('%J',df.Journal[i],file=open("bib.txt", "a"))
            print('%V',str(df.Volume[i]),file=open("bib.txt", "a"))
            print('%N',df.Issue[i],file=open("bib.txt", "a"))
            print('%P',df.Page[i],file=open("bib.txt", "a"))
            print('%D',int(df.Year[i]),file=open("bib.txt", "a"))
            print("",file=open("bib.txt", "a"))
        
        print("A new refer bibliography file (bib.txt) has been created.",
              "No changes were made to the existing df.csv file")

    else:
        title1()
        
    title1()
            
print("Welcome to litfinder. Please select an option below:")
title1()
