from bs4 import BeautifulSoup
import urllib.request
import os
import eel

import re
eel.init("")
firstLoad = True
counter = 0

#https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard
def getBorne():
    with urllib.request.urlopen('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard') as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

@eel.expose
def getLinks(borneUrl): #la borneUrl est en réalité la fin de l'url d'une page wikipedia
    validLinks = []
    with urllib.request.urlopen("https://fr.wikipedia.org/wiki/{}".format(borneUrl)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')

        global firstLoad
        global newLink
        global counter

        if firstLoad:
            oldLink = ''
            firstLoad = False
        else:
            oldLink = newLink

        newLink = soup.find("h1").get_text()
        print(newLink)
        print(oldLink)
        
        div = soup.find("div", {"id": "mw-content-text"})
        allLinks = div.find_all("a")

        allGoodLinks = []
        for i in allLinks:
            iString = str(i)
            if '/wiki/' in iString and ':' not in iString:
                allGoodLinks.append(i)

        allGoodLinksUnique = list(dict.fromkeys(allGoodLinks))

        allGoodLinksTitre = []
        for i in allGoodLinksUnique:
            text = str(i)
            m = re.search('>(.+?)</a>', text)
            if m:
                allGoodLinksTitre.append(m.group(1)) 
        
        allGoodLinksUrl = []
        for i in allGoodLinksUnique:
            text = str(i)
            m = re.search('/wiki/(.+?)"', text)
            if m:
                allGoodLinksUrl.append(m.group(1))


        #création de l'html et insertion des données
        currentPath = os.path.dirname(__file__)
        currentPath = os.path.join(currentPath,"wiki.html")
        f = open(currentPath,'w+', encoding='utf-8')
        f.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Wikigame</title>    
            <script type="text/javascript" src="/eel.js"></script>
        </head>
            <body>
            <h3>Essai numéro : {}</h3>
            <h1>{}</h1>
            <h2>{}</h2>
        """.format(counter, newLink, oldLink))
        for i in range(len(allGoodLinksUnique)):
            f.write("""        <button onclick="nextPage('{}')">{}</button><br>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
                
        f.write("""
                <script>
                    const nextPage = (url) => {
                        eel.getLinks(url)
                        document.location.reload();
                    }
                </script>
            </body>
        </html>
        """)
        f.close()
        counter = counter + 1


firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

print("{} > {}".format(firstBorne, lastBorne))
getLinks(firstBorneUrl)

eel.start('wiki.html', mode="chrome-app")
