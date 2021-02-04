#WikiGame, par Théo Migeat
#Import des lib
from bs4 import BeautifulSoup
import urllib.request
import os
import eel
import time

import re

#Initialisation des variables globales
eel.init("")
firstLoad = True
counter = 0
allLinksVisited = []
allTitlesVisited = []

#Fonction renvoyant l'url d'une page au pif ainsi que son titre
def getBorne():
    global firstLoad
   
    if(firstLoad):
        cleanUrl = urllib.parse.quote('https://fr.wikipedia.org/wiki/Spécial:Page_au_hasard', safe=':/')
    else:
        cleanUrl = 'https://fr.wikipedia.org/wiki/Spécial:Page_au_hasard'
    with urllib.request.urlopen(cleanUrl) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

firstBorne = "Gnocchi"
firstBorneUrl = "Gnocchi"
lastBorne = "Italie"
lastBorneUrl = "Italie"

#GetLinks permet à partir d'un lien wiki de générer une page html avec tous les liens et d'autres trucs
@eel.expose #Pour qu'on puisse appeller la fonction dans le js de l'html que l'on génère
def getLinks(borneUrl, counterPoints = 1, addTab = True): #la borneUrl est en réalité la fin de l'url d'une page wikipedia
    global firstLoad
    
    validLinks = []
    if(firstLoad or not("%" in borneUrl)):
        print('Formatage du lien !')
        cleanUrl = urllib.parse.quote("https://fr.wikipedia.org/wiki/{}".format(borneUrl), safe=':/')
    else:
        print('Lien ok, pas besoin de formater')
        cleanUrl = "https://fr.wikipedia.org/wiki/{}".format(borneUrl)
    print(firstLoad)
    print(cleanUrl)
    with urllib.request.urlopen(cleanUrl) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        
        global newLink
        global counter

        global firstBorne
        global firstBorneUrl
        global lastBorne
        global lastBorneUrl

        newLink = soup.find("h1").get_text()

        if(newLink == lastBorne):
            if(firstLoad):
                firstBorne, firstBorneUrl = getBorne()
                lastBorne, lastBorneUrl = getBorne()
                getLinks(firstBorneUrl)
            else:
                print("Victoire !")
                endGame()
        else:
            div = soup.find("div", {"id": "mw-content-text"})
            allLinks = div.find_all("a")

            allGoodLinks = []
            for i in allLinks:
                iString = str(i)
                if "/wiki/" in iString and ':' not in iString and "src=" not in iString:
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

            if addTab:
                print("Génération du tableau : {}".format(borneUrl))
                allLinksVisited.append(borneUrl)
                allTitlesVisited.append(newLink)
            else:
                allLinksVisited.pop()
                allTitlesVisited.pop()

            print(allTitlesVisited)
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
                <link rel="preconnect" href="https://fonts.gstatic.com">
                <link href="https://fonts.googleapis.com/css2?family=Open+Sans&family=PT+Serif&display=swap" rel="stylesheet">
                <link rel="stylesheet" href="style.css">
                <script src="https://kit.fontawesome.com/373a1c097b.js" crossorigin="anonymous"></script>
                <script type="text/javascript" src="/eel.js"></script>
            </head>
                <body>
                <aside class="loading hide">Chargement...</aside>
                <nav>
                    <p>{} > {}<p/>
                </nav>
                <header>
                    <section>
                        <h1>{}</h1>
                    </section>
                    <section>
                        <h1 class="counter">Coup n°{}</h1>
                    </section>
                </header>""".format(firstBorne, lastBorne, newLink, counter))
            if len(allLinksVisited) > 1:
                f.write("""
                <div class='previous-div'>
                    <h2>Page d'avant : {}</h2>
                    <button onclick="goBackJS(`{}`)"><i class="fas fa-backward"></i>Revenir en arrière ? (coute deux coups)</button>
                </div>
                """.format(allTitlesVisited[-2], allLinksVisited[-2])) #allLinksVisited[-1] représente le dernier lien du tableau de tous les liens parcouru
            f.write('<article class="wiki-links">')
            for i in range(len(allGoodLinksUnique)):
                f.write("""        <section onclick='nextPage(`{}`)'><p>{}</p></section>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
            f.write("""
            </article>
                    <script>
                        const hideLinks = document.querySelector('.wiki-links');
                        const loading = document.querySelector('.loading');

                        eel.expose(reloadPage);
                        function reloadPage() {
                         document.location.reload();
                        }

                        const hideLinksFunction = () => {
                            hideLinks.classList.add('hide');
                            loading.style.animationPlayState = "running";
                            loading.classList.remove('hide');
                        }

                        const nextPage = (url) => {
                            hideLinksFunction();
                            eel.getLinks(url);
                        }

                        const goBackJS = (url) => {
                            hideLinksFunction();
                            eel.goBack(url);
                        }
                    </script>
                </body>
            </html>
            """)
            f.close()
            if not firstLoad:
                try:
                    eel.reloadPage()
                except:
                    print("YA EU L'ERREUR AAAAAAAAAAAAAA")
                    time.sleep(2)
                    eel.reloadPage()
            else:
                firstLoad = False

@eel.expose
def goBack(url):
    getLinks(url, 2, False)


def endGame():
    allTitlesVisited.append(lastBorne)
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
        <title>Wikigame | Victoire !</title>    
        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans&family=PT+Serif&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
        <script src="https://kit.fontawesome.com/373a1c097b.js" crossorigin="anonymous"></script>
        <script type="text/javascript" src="/eel.js"></script>
    </head>
        <body>
        <nav>
            <p>{} > {}<p/>
        </nav>
        <div class="victory-div">
            <h1>Victoire !<h1>
            <h2>Il vous a fallu {} {}</h2>
            <p>""".format(firstBorne, lastBorne, counter, "coup" if counter < 2 else "coups" ))
    for i in range(len(allTitlesVisited)):
        if(i != len(allTitlesVisited) - 1):
            f.write("""        <span>{} ></span>""".format(allTitlesVisited[i]))
        else:
            f.write("""        <span>{}</span>""".format(allTitlesVisited[i]))
    f.write(""" 
        </p>
        </div>
        </body>
    </html>
    """)

    f.close()
    eel.reloadPage()

print("{} > {}".format(firstBorne, lastBorne))
getLinks(firstBorneUrl)

eel.start('wiki.html', mode="chrome-app")
