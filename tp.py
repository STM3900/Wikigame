from bs4 import BeautifulSoup
import urllib.request
import os
import eel

import re


#https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard
def getBorne():
    with urllib.request.urlopen('https://fr.wikipedia.org/wiki/Jean_Journet') as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

def getLinks():
    validLinks = []
    with urllib.request.urlopen("https://fr.wikipedia.org/wiki/{}".format(firstBorneUrl)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        div = soup.find("div", {"id": "mw-content-text"})
        allLinks = div.find_all("a")

        print("AVANT MODIFICATIONS")
        print("\n\n")
        allGoodLinks = []
        for i in allLinks:
            iString = str(i)
            if '/wiki/' in iString and ':' not in iString:
                print("LIEN CORRECT") #plus poli, pour moins énerver le code 
                print("-----------------------")
                print(i)
                print("-----------------------")
                allGoodLinks.append(i)

        print("\n\n")
        print("APRES MODIFICATIONS - NON FILTRÉ")

        allGoodLinksUnique = list(dict.fromkeys(allGoodLinks))
        allLinksTitle = []

        if allGoodLinksUnique != allGoodLinks:
            print("DOUBLON DÉTECTÉ")

        for i in allGoodLinksUnique:
            print(i)

        for i in allGoodLinksUnique:
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