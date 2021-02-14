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
currentPage = ""
allLinksVisited = []
allTitlesVisited = []
newTitle = ""
currentUrl = ""
div = ""

counterIncrement = 1
addTab = True

#Fonction permetant de renvoyer un lien formaté, et prêt ) étre utilisé par urlopen
def formatLink(link = "Spécial:Page_au_hasard"):
    global firstLoad
    if(firstLoad or not('%' in link)):
        print('Formatage du lien !')
        cleanUrl = urllib.parse.quote("https://fr.wikipedia.org/wiki/{}".format(link), safe=':/')
    else:
        print('Lien ok, pas besoin de formater')
        cleanUrl = "https://fr.wikipedia.org/wiki/{}".format(link)

    return cleanUrl

#Fonction renvoyant l'url d'une page au pif ainsi que son titre
def getBorne():
    with urllib.request.urlopen(formatLink()) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

def checkEndGame(title):
    global firstBorne
    global firstBorneUrl
    global lastBorne
    global lastBorneUrl

    if title == lastBorne:
        if firstLoad:
            firstBorne, firstBorneUrl = getBorne()
            lastBorne, lastBorneUrl = getBorne()
            getLinks(firstBorneUrl)
        else:
            print("Victoire !")
            endGame()
    else:
        loadpage()

def decomposeInvalidElements():
    global div

    toolBox = div.find_all("div", {"class": "bandeau-container"})
    if(toolBox == None):
        print("pas de bandeau détecté, tout va bien")
    else:
        print("bandeau détecté, on le tej")
        for i in range(len(toolBox)):
            toolBox[i].decompose()

    asideMenu = div.find("div", {"class": "infobox_v3"})
    if(asideMenu == None):
        print("Pas de menu v3 détecté, tranquille")
        asideMenu = div.find("table", {"class": ["infobox_v2", "infobox", "DebutCarte"]})
        if(asideMenu != None):
            asideMenu.decompose()
    else:
        print("Menu v3 détecté, on le tej")
        asideMenu.decompose()

def getDescription(div):
    description2 = div.find("p", {"class": None})

    descriptionStyle = description2.find("style")
    if(descriptionStyle != None):
        descriptionStyle.decompose()

    description = description2.find_all(text=True)
    descriptionFinal = []

    descCounter = 0
    for i in description:
        iString = str(i)
        if not((iString == '[' and description[descCounter + 1].isdigit()) or iString.isdigit() or (iString == ']' and description[descCounter - 1].isdigit()) or (iString == ',' and description[descCounter - 1] == ']' and description[descCounter + 1] == '[')):
            descriptionFinal.append(i)
        descCounter = descCounter + 1

    
    descdescriptionFinal = ''.join(descriptionFinal)
    descdescriptionFinal = descdescriptionFinal.replace("(Écouter)", '')
    descdescriptionFinal = descdescriptionFinal.replace(" ,", ',')
    return descdescriptionFinal

def openPage(url):
    with urllib.request.urlopen(formatLink(url)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')

        global newTitle
        global currentUrl
        newTitle = soup.find("h1").get_text()
        currentUrl = url

    return soup

def getWikiLinks(allLinks):
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

    return allGoodLinksUnique, allGoodLinksTitre, allGoodLinksUrl

def addLinkTitle(addTab):
    global allLinksVisited
    global allTitlesVisited

    if addTab:
        print("Génération du tableau : {}".format(currentUrl))
        allLinksVisited.append(currentUrl)
        allTitlesVisited.append(newTitle)
    else:
        allLinksVisited.pop()
        allTitlesVisited.pop()

#TODO : terminer la fonction openPage et faire celle pour afficher tous les trucs tavu et continuer la fonction chelou de loadpage
def loadpage():
    global currentPage
    global newTitle
    global currentUrl
    global counter
    global firstLoad
    global div

    global counterIncrement
    global addTab

    print(currentUrl)

    div = currentPage.find("div", {"id": "mw-content-text"})
    allLinks = div.find_all("a")

    decomposeInvalidElements()
    descdescriptionFinal = getDescription(div)

    allGoodLinksUnique, allGoodLinksTitre, allGoodLinksUrl = getWikiLinks(allLinks)
    addLinkTitle(addTab)

    print(allTitlesVisited)
    #création de l'html et insertion des données
    counter = counter + counterIncrement
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
        <script src="js/reload.js"></script>
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
        </header>
        <p class="description">{}<p>""".format(firstBorne, lastBorne, newTitle, counter, descdescriptionFinal))
    if len(allLinksVisited) > 1:
        f.write("""
        <div class='previous-div'>
            <h2>Page précédente : {}</h2>
            <button onclick="goBackJS(`{}`)"><i class="fas fa-backward"></i>Revenir en arrière ? (coute deux coups)</button>
        </div>
        """.format(allTitlesVisited[-2], allLinksVisited[-2])) #allLinksVisited[-1] représente le dernier lien du tableau de tous les liens parcouru
    f.write("""
        <article class="wiki-links">""")
    for i in range(len(allGoodLinksUnique)):
        try:
            f.write("""        <section onclick='nextPage(`{}`)'><p>{}</p></section>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
        except:
            print("Erreur de out of range, mais je sais pas pourquoi ça a lieu")
    f.write("""
    </article>
            <script src="js/main.js"></script>
        </body>
    </html>
    """)
    f.close()
    if not firstLoad:
        try:
            eel.reloadPage()
        except:
            print("YA EU L'ERREUR AAAAAAAAAAAAAA")
            time.sleep(1)
            getLinks(currentUrl)
    else:
        firstLoad = False

    counterIncrement = 1
    addTab = True

    print("\n")


#!FONCTION QUI FAIT TOUT COMMENCER
@eel.expose
def initiate(Linkurl):
    global currentPage
    currentPage = openPage(Linkurl)

    global newTitle
    checkEndGame(newTitle)

#GetLinks permet à partir d'un lien wiki de générer une page html avec tous les liens et d'autres trucs
@eel.expose #Pour qu'on puisse appeller la fonction dans le js de l'html que l'on génère
def getLinks(borneUrl, counterPoints = 1, addTab = True): #la borneUrl est en réalité la fin de l'url d'une page wikipedia
    with urllib.request.urlopen(formatLink(borneUrl)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        
        global newTitle
        global counter
        global firstLoad

        global firstBorne
        global firstBorneUrl
        global lastBorne
        global lastBorneUrl

        if(newTitle == lastBorne):
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

            toolBox = div.find_all("div", {"class": "bandeau-container"})
            if(toolBox == None):
                print("pas de bandeau détecté, tout va bien")
            else:
                print("bandeau détecté, on le tej")
                for i in range(len(toolBox)):
                    toolBox[i].decompose()


            asideMenu = div.find("div", {"class": "infobox_v3"})
            if(asideMenu == None):
                print("Pas de menu v3 détecté, tranquille")
                asideMenu = div.find("table", {"class": ["infobox_v2", "infobox", "DebutCarte"]})
                if(asideMenu != None):
                    asideMenu.decompose()
            else:
                print("Menu v3 détecté, on le tej")
                asideMenu.decompose()

            description2 = div.find("p", {"class": None})
            #print(description2)

            descriptionStyle = description2.find("style")
            if(descriptionStyle != None):
                descriptionStyle.decompose()

            description = description2.find_all(text=True)
            descriptionFinal = []

            descCounter = 0
            for i in description:
                iString = str(i)
                if not((iString == '[' and description[descCounter + 1].isdigit()) or iString.isdigit() or (iString == ']' and description[descCounter - 1].isdigit()) or (iString == ',' and description[descCounter - 1] == ']' and description[descCounter + 1] == '[')):
                    descriptionFinal.append(i)
                descCounter = descCounter + 1

            
            descdescriptionFinal = ''.join(descriptionFinal)
            #print(descdescriptionFinal)
            descdescriptionFinal = descdescriptionFinal.replace("(Écouter)", '')
            descdescriptionFinal = descdescriptionFinal.replace(" ,", ',')
            #print(descdescriptionFinal)
            
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
                allTitlesVisited.append(newTitle)
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
                <script src="js/reload.js"></script>
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
                </header>
                <p class="description">{}<p>""".format(firstBorne, lastBorne, newTitle, counter, descdescriptionFinal))
            if len(allLinksVisited) > 1:
                f.write("""
                <div class='previous-div'>
                    <h2>Page précédente : {}</h2>
                    <button onclick="goBackJS(`{}`)"><i class="fas fa-backward"></i>Revenir en arrière ? (coute deux coups)</button>
                </div>
                """.format(allTitlesVisited[-2], allLinksVisited[-2])) #allLinksVisited[-1] représente le dernier lien du tableau de tous les liens parcouru
            f.write("""
                <article class="wiki-links">""")
            for i in range(len(allGoodLinksUnique)):
                try:
                    f.write("""        <section onclick='nextPage(`{}`)'><p>{}</p></section>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
                except:
                    print("Erreur de out of range, mais je sais pas pourquoi ça a lieu")
            f.write("""
            </article>
                    <script src="js/main.js"></script>
                </body>
            </html>
            """)
            f.close()
            if not firstLoad:
                try:
                    eel.reloadPage()
                except:
                    print("YA EU L'ERREUR AAAAAAAAAAAAAA")
                    time.sleep(1)
                    getLinks(borneUrl)
            else:
                firstLoad = False
            print("\n\n\n")

@eel.expose
def goBack(url):
    global counterIncrement
    global addTab

    counterIncrement = 2
    addTab = False
    
    initiate(url)


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
#getLinks(firstBorneUrl)
initiate(firstBorneUrl)

eel.start('wiki.html', mode="chrome-app")
