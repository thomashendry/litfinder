#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 11:13:49 2021

@author: thomas hendry 2021
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
    print("7: Exit")
    
    option1 = int(input("Option: "))
    
    if option1 == 1:
        googlesearch1()    
    elif option1 == 0:
        csvcreate()
    elif option1 == 2:
        scopus_search()
    elif option1 == 4:
        abdccheck()
    elif option1 == 7:
        quit()
        
def csvcreate():
    import csv
    print("By proceeding, a new csv file is created to store your results.")
    proceed1 = str(input('Proceed (y/n)?: '))
    if proceed1 == 'y':
        with open('df.csv', 'w') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['Program', 'Query', 'Title', 'Author',
                                     'Year', 'Volume', 'Issue', 'Page',
                                     'Journal', 'Snippet', 'URL'])
        print('Okay, a new csv file (df.csv) has been created!')
        title1()
    if proceed1 == 'n':
        title1()
    else:
        print("Sorry, that is not a valid option. Please type 'y' or 'n' (lowercase)")
        title1()
        
def googlesearch1():
    
    def googlesearch(QUERY,QUERY_NUM,YEARS,FILETYPE,LOCATION,PAGE):
        import requests
        from csv import writer
    
        start = (PAGE - 1) * 10 + 1
    
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={QUERY}&start={start}&dateRestrict=y[{YEARS}]&fileType={FILETYPE}&gl={LOCATION}"

        data = requests.get(url).json()

        # get the result items
        search_items = data.get("items")
    
        # iterate over 10 results found
        for i, search_item in enumerate(search_items, start=1):
        
            title = search_item.get("title")
            snippet = search_item.get("snippet")
            link = search_item.get("link")
            print("="*10, f"Result #{i+start-1}", "="*10)
            print("Title:", title)
            print("Description:", snippet)
            print("URL:", link, "\n")
            
            r = requests.get(link, timeout=300000)
            
            with open(str(QUERY_NUM)+"_"+str(title),'wb') as f:
                f.write(r.content)
                
            list=['Google',QUERY,title,'-','-',snippet, link]
            
            with open('df.csv','a',newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(list)
                f_object.close()

        print("These results are now saved on your computer!")

        CONT = str(input("Continue search (y/n)?: "))

        if CONT == 'y':
            PAGE = PAGE + 1
            googlesearch(QUERY,QUERY_NUM,YEARS,FILETYPE,LOCATION,PAGE)
    
        elif CONT == 'n':
            print("Finished")
            print("")
            title1()
 
    API_KEY = "API KEY HERE"
    SEARCH_ENGINE_ID = "SEARCH ENGINE ID"
    print("Google Downloader searches Google (not Google Scholar) for files according to a specified query.",
          "These files are saved locally. The csv file is also updated with file information.")
    QUERY = str(input("Type your query: "))
    QUERY_NUM = int(input("Enter a query number for your reference: "))
    YEARS = int(input("How many years back would you like to search?: "))
    FILETYPE = str(input("What file type would you like (i.e. pdf, doc etc.)?: "))
    LOCATION = str(input("What location would you like to search from (i.e. au, us etc.)?: "))
    PAGE = int(input("What page from the search?: "))

    googlesearch(QUERY,QUERY_NUM,YEARS,FILETYPE,LOCATION,PAGE)

def scopus_search():
    
    from pybliometrics.scopus import ScopusSearch
    import pandas as pd
    import os
    print("Scopus Search searches Scopus for files according to a specified query.",
          "The csv file is updated with file information. ",
          "Currently, pdf versions are not saved locally.",
          "Refer to Scopus for field codes.")
    QUERY_SCOPUS = str(input("Type your query: "))
    
    s = ScopusSearch(QUERY_SCOPUS, subscriber=True)
    
    df = pd.DataFrame(pd.DataFrame(s.results))
    df['Program'] = 'Scopus'
    df['Query'] = QUERY_SCOPUS
    df = df[['Program','Query','title','author_names','coverDate',
             'volume','issueIdentifier','pageRange','publicationName',
             'description','doi']]
    df['doi'] = str('https://www.doi.org/')+df['doi'] 
    df.rename(columns = {'title':'Title','author_names':'Author','coverDate':'Year',
                         'volume':'Volume','issueIdentifier':'Issue','pageRange':'Page',
                         'publicationName':'Journal','description':'Snippet',
                         'doi':'URL'},inplace = True)
    df['Year'] = df['Year'].astype(str).str[:4]
    
    print('The search found',len(df.Year),'results. The file df.csv has been updated.')
    df.to_csv('df_scopus.csv')

    df1 = pd.read_csv("df.csv")
    df2 = pd.read_csv("df_scopus.csv")
    pd.concat([df1, df2]).to_csv('df.csv', index=False)
    os.remove("df_scopus.csv")
    title1()

#%%
def abdcreduce():
    import pandas as pd
    journals = pd.read_csv('journals.csv')
    journals = journals[['Title', 'Rating']]
    journals.rename(columns = {'Title':'Journal'},inplace = True)
    results = pd.read_csv('df_abdc.csv')
    results2 = pd.merge(results, journals)
    df = results2[['Program','Query','Title','Author','Year','Volume',
                   'Issue','Page','Journal','Snippet','URL','Rating']]
    
    print("You can now remove papers according to the rating of their corresponding journal.",
          "Type c to remove C and below, type b to remove B and below etc.")
    cutoff = str(input("What rating would you like to remove (a, b or c)?: "))
    
    if cutoff == 'keep all':
        df.to_csv("df_abdc_all.csv")
    elif cutoff == 'c':
        dfabovec = df.loc[df.Rating != 'C']
        dfabovec.to_csv("df_abdc_noC")
    elif cutoff == 'b':
        dfaboveb = df.loc[(df.Rating != 'C') & (df.Rating != 'B')]
        dfaboveb.to_csv("df_abdc_noBC")
    elif cutoff == 'a':
        dfabovea = df.loc[(df.Rating != 'C') & (df.Rating != 'B') & (df.Rating != 'A')]
        dfabovea.to_csv("df_abdc_noABC")

    print("A new csv file has been created based on the ratings you specified.")
    title1()

def abdccheck():
    import pandas as pd
    import numpy as np
    print("This will remove all papers printed in journals not rated by ABDC.")
    journals = pd.read_csv("journals.csv")
    searches = pd.read_csv("df.csv")
    print("Your searches have resulted in", len(searches), "papers.")
    searches["Ranked"] = np.where(searches.Journal.isin(journals.Title), True, False)
    searches2 = searches[searches.Ranked == True]
    print("The new csv file (df_abdc.csv) will have", len(searches2), "papers.")
    goahead = str(input("Proceed (y/n)?: "))
    
    if goahead == 'y':
        searches2.to_csv("df_abdc.csv")
        abdcreduce()
    else:
        title1()

print("Welcome to litfinder. Please select an option below:")
title1()
