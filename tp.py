from bs4 import BeautifulSoup
import urllib.request
import os
import eel


#https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard
def getBorne():
    with urllib.request.urlopen('https://fr.wikipedia.org/wiki/Brock_Boeser') as response:
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

        for i in allLinks:
            print(i)
            if 'href="#' in str(i):
                print("LIEN DE MERDE")
            counter = counter + 1
        

firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

print("{} > {}".format(firstBorne, lastBorne))
getLinks()



"""
currentPath = os.path.dirname(__file__)
currentPath = os.path.join(currentPath,"wiki.html")
f = open(currentPath,'w+', encoding='utf-8')
"""