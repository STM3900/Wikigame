from bs4 import BeautifulSoup
import urllib.request
import os
import eel

import re


#https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard
def getBorne():
    with urllib.request.urlopen('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard') as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

def getLinks():
    counter = 0
    validLinks = []
    with urllib.request.urlopen("https://fr.wikipedia.org/wiki/{}".format(firstBorneUrl)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        div = soup.find("div", {"id": "bodyContent"})
        allLinks = div.find_all("a")

        print("AVANT MODIFICATIONS")
        print("\n\n")
        for i in allLinks:
            #print(i)
            if 'href="#' in str(i) or ':' in str(i) or '/w/' in str(i):
                #print("LIEN INCORRECT") #plus poli, pour moins énerver le code 
                allLinks.pop(counter)
            counter = counter + 1

        print("\n\n")
        print("APRES MODIFICATIONS - NON FILTRÉ")

        allLinks2 = list(dict.fromkeys(allLinks))
        allLinksTitle = []

        if allLinks2 != allLinks:
            print("DOUBLON DÉTECTÉ")

        for i in allLinks2:
            print(i)

        for i in allLinks2:
            text = str(i)
            m = re.search('>(.+?)</a>', text)
            if m:
                found = m.group(1)
            print(found)
            


        

firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

print("{} > {}".format(firstBorne, lastBorne))
getLinks()



"""
currentPath = os.path.dirname(__file__)
currentPath = os.path.join(currentPath,"wiki.html")
f = open(currentPath,'w+', encoding='utf-8')
"""