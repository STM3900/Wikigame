#WikiGame, par Théo Migeat
#Import des lib
from bs4 import BeautifulSoup
import urllib.request
import os
import eel

import re

#Initialisation des variables globales
eel.init("")
firstLoad = True
counter = 0
allLinksVisited = []

#Fonction renvoyant l'url d'une page au pif ainsi que son titre
def getBorne():
    with urllib.request.urlopen('https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard') as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

#GetLinks permet à partir d'un lien wiki de générer une page html avec tous les liens et d'autres trucs
@eel.expose #Pour qu'on puisse appeller la fonction dans le js de l'html que l'on génère
def getLinks(borneUrl, counterPoints = 1): #la borneUrl est en réalité la fin de l'url d'une page wikipedia
    print(borneUrl)
    print(lastBorneUrl)
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

        if(newLink == lastBorne):
            endGame()
        else:
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
            counter = counter + counterPoints
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
                <h2>{} > {}<h2>
                <h3>Essai numéro : {}</h3>
                <h1>{}</h1>""".format(firstBorne, lastBorne, counter, newLink))
            if len(allLinksVisited) > 1:
                f.write("""
                <h2>Page d'avant : {}</h2>
                <button onclick="goBackJS(`{}`)">Revenir en arrière ? (coute deux coups)</button>
                """.format(oldLink, allLinksVisited[-1])) #allLinksVisited[-1] représente le dernier lien du tableau de tous les liens parcouru
            for i in range(len(allGoodLinksUnique)):
                f.write("""        <button onclick="nextPage(`{}`)">{}</button><br>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
                    
            f.write("""
                    <script>
                        const nextPage = (url) => {
                            eel.getLinks(url)
                            document.location.reload();
                        }

                        const goBackJS = (url) => {
                            eel.getLinks(url, 2)
                            document.location.reload();
                        }
                    </script>
                </body>
            </html>
            """)
            f.close()
            allLinksVisited.append(borneUrl)

def endGame():
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
        <h1>Bravo ! Vous êtes arrivé sur la bonne page ! ({} > {})<h1>
        <h2>Il vous a fallu {} essai(s)</h2>
        </body>
    </html>
    """.format(firstBorne, lastBorne, counter))

            

    f.close()

firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

allLinksVisited.append(firstBorneUrl)

print("{} > {}".format(firstBorne, lastBorne))
getLinks(firstBorneUrl)

eel.start('wiki.html', mode="chrome-app")
