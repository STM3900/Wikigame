#--------------------------------------------
# WikiGame, par Théo Migeat - version 2
#--------------------------------------------

# Import des lib
from bs4 import BeautifulSoup
import urllib.request
import os
import eel

# Import des fonctions pour utliser les regex (il n'y en a pas beaucoup ne vous en faites pas)
import re

# Initialisation de eel
eel.init("")

#--------------------------------------------
# Initialisation des variables globales
#--------------------------------------------

firstLoad = True # Variable uniquement sur True lors du lancement du jeu
counter = 0 # Valeur du compteur de coups
currentPage = "" # Page html dans laquelle l'utilisateur est
div = "" # Div html de la page actuelle
allLinksVisited = [] # Tableau contenant tous les liens des pages visitées
allTitlesVisited = [] # Tableau contenant tous les titres des pages visitées
currentTitle = "" # Titre de la page actuelle
currentUrl = "" # Litre de la page actuelle
counterIncrement = 1 # Incrément du counter, de base à 1 mais à deux quand on reviens en arière
addTab = True # Détermine si le lien et le titre d'une page et ajouté dans les tableaux ci dessus


#--------------------------------------------
# Fonctions
#--------------------------------------------

# Fonction permetant de renvoyer un lien formaté et prêt a être utilisé
def formatLink(link = "Spécial:Page_au_hasard"):
    global firstLoad
    if(firstLoad or not('%' in link)):
        print('Formatage du lien !')
        cleanUrl = urllib.parse.quote("https://fr.wikipedia.org/wiki/{}".format(link), safe=':/')
    else:
        print('Lien ok, pas besoin de formater')
        cleanUrl = "https://fr.wikipedia.org/wiki/{}".format(link)

    return cleanUrl

# Fonction renvoyant l'url d'une page au pif ainsi que son titre
def getBorne():
    with urllib.request.urlopen(formatLink()) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
        h1 = soup.find("h1").get_text()
        h1Url = h1.replace(" ", "_")
        return h1, h1Url

# Vérifie si l'utilisateur a gagné
# - Si il gagne, le renvoie sur la fonction endGame
# - Sinon, lui fait charger la page
def checkEndGame(title):
    global firstBorne
    global firstBorneUrl
    global lastBorne
    global lastBorneUrl

    # On fait la vérification en comparant les deux titres des pages, 
    # car les liens peuvent avoir plusieurs variantes en fonction du formatage
    if title == lastBorne:
        # Dans le cas improbable ou les deux bornes sont identiques, les rechanger et relancer 
        # (si même après ça les deux bornes sont identiques, jouez au loto immédiatement)
        if firstLoad:
            firstBorne, firstBorneUrl = getBorne()
            lastBorne, lastBorneUrl = getBorne()
            initiate(firstBorneUrl)
        else:
            print("Victoire !")
            endGame()
    else:
        loadpage()

# Génère la page html en indiquant au joueur qu'il a gagné, mais aussi :
# - Son nombre de coups
# - Son parcours (C'est grace à allTitlesVisited que cela est possible)
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

# En prenant une url wiki, ouvre sa page wiki et renvoie l'instance soup
def openPage(url):
    with urllib.request.urlopen(formatLink(url)) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')

        #On modifie les valeurs globales du titre et du lien, 
        # elles seront utilisées dans d'autres fonctions
        global currentTitle
        global currentUrl
        currentTitle = soup.find("h1").get_text()
        currentUrl = url

    return soup

# Utilise la div globale et lui enlève les éléments non voulu (bandeau d'entête et panneau latéral)
def decomposeInvalidElements():
    global div

    toolBox = div.find_all("div", {"class": "bandeau-container"})
    if(toolBox == None):
        print("pas de bandeau détecté, pas de modifs requises")
    else:
        print("bandeau détecté, suppression...")
        for i in range(len(toolBox)):
            toolBox[i].decompose()

    asideMenu = div.find("div", {"class": "infobox_v3"})
    if(asideMenu == None):
        print("Pas de menu v3 détecté, pas de modifs requises")
        asideMenu = div.find("table", {"class": ["infobox_v2", "infobox", "DebutCarte"]})
        if(asideMenu != None):
            asideMenu.decompose()
    else:
        print("Menu v3 détecté, suppression...")
        asideMenu.decompose()

# (Bonus)
# Récupère le premier paragraphe de la page, en le formatant pour éviter au maximum les caractères des faux liens
# La fonction renvoie un string de la description
def getDescription(div):
    description2 = div.find("p", {"class": None})

    # Il arrive que des pages n'aient pas de descriptions d'intro (Comme celle de Septembre 1979)
    try:
        descriptionStyle = description2.find("style")
    except:
        print("ERREUR : Aucune description")
        descdescriptionFinal = ''
    else:
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

# A partir d'une liste contenant tous les liens, renvoi :
# - Une liste contenant tous les liens valides (sans doublons)
# - Une liste de tous les titres valides
# - Une liste de tous les liens valides
#! Cette fontion fait partie du coeur du programme
def getWikiLinks(allLinks):
    allGoodLinks = []
    for i in allLinks:
        iString = str(i)
        if "/wiki/" in iString and ':' not in iString and "src=" not in iString:
            allGoodLinks.append(i)

    allGoodLinksUnique = list(dict.fromkeys(allGoodLinks)) # Un dictionnaire ne peut pas avoir de clés identiques, donc il les supprime automatiquement

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

# Selon la valeur de addTab (True ou False) :
# - Ajoute le titre et le lien dans leurs liste respectives
# - Supprime le dernier élément de leurs liste pour préparer le retour en arrière
def addLinkTitle(addTab):
    global allLinksVisited
    global allTitlesVisited

    if addTab:
        print("Génération du tableau : {}".format(currentUrl))
        allLinksVisited.append(currentUrl)
        allTitlesVisited.append(currentTitle)
    else:
        allLinksVisited.pop()
        allTitlesVisited.pop()

# A partir d'un fichier, du titre actuel, du compteur et de la description,
# génère le début du fichier html
def writeBeginningHtml(file, currentTitle, counter, descdescriptionFinal):
    file.write("""
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
        <script type="text/javascript" src="/eel.js"></script> <!--Lancement d'eel, qui permet de faire discuter le js et le python autour d'une tasse de code-->
        <script src="js/reload.js"></script> <!--Import du fichier reload.js qui contient la fonction reload-->
    </head>
        <body>
        <aside class="loading hide">Chargement...</aside>
        <nav>
            <p>{} > {}</p>
        </nav>
        <header>
            <section>
                <h1>{}</h1>
            </section>
            <section>
                <h1 class="counter">Coup n°{}</h1>
            </section>
        </header>
        <p class="description">{}<p>""".format(firstBorne, lastBorne, currentTitle, counter, descdescriptionFinal))

@eel.expose # eel.expose rend la fonction accessible en js
# (Bonus)
# Fonction permetant de revenir en arière d'une page, mais qui coute deux coups à son utilisateur
def goBack(url):
    global counterIncrement
    global addTab

    counterIncrement = 2
    addTab = False

    initiate(url)

# (Bonus)
# à partir d'un fichier génère la partie permettant au joueur de revenir en arrière
def writeGoBackhtml(file):
        file.write("""
        <div class='previous-div'>
            <h2>Page précédente : {}</h2>
            <button onclick="goBackJS(`{}`)"><i class="fas fa-backward"></i>Revenir en arrière ? (coute deux coups)</button>
        </div>
        """.format(allTitlesVisited[-2], allLinksVisited[-2])) #allLinksVisited[-1] représente le dernier lien du tableau de tous les liens parcouru

# à partir d'un fichier, et des listes des liens valides, génère la fin du fichier html
def writeEndHtml(file, allGoodLinksUnique, allGoodLinksUrl, allGoodLinksTitre):
    file.write("""
        <article class="wiki-links">""")
    for i in range(len(allGoodLinksUnique)):
        # Il arrive d'avoir une erreur de out of range, mais celle-ci n'altère pas le fonctionnement du code
        try:
            file.write("""        <section onclick='nextPage(`{}`)'><p>{}</p></section>\n""".format(allGoodLinksUrl[i], allGoodLinksTitre[i]))
        except:
            print("Erreur de out of range")
    file.write("""
    </article>
            <script src="js/main.js"></script> <!--Ici on appelle le fichier js contenant les fonctions js-->
        </body>
    </html>
    """)
    file.close()

#! COEUR DU PROGRAMME
# Fonction permettant de générer la page
# (elle appelle une grosse partie des fonctions ci-dessus)
def loadpage():
    # Appel des variables globales
    global currentPage
    global currentTitle
    global currentUrl
    global counter
    global firstLoad
    global div

    global counterIncrement
    global addTab

    print(currentUrl)

    # Génération de la div et formatage des liens    
    div = currentPage.find("div", {"id": "mw-content-text"})
    allLinks = div.find_all("a")

    decomposeInvalidElements()
    descdescriptionFinal = getDescription(div)

    allGoodLinksUnique, allGoodLinksTitre, allGoodLinksUrl = getWikiLinks(allLinks)
    addLinkTitle(addTab)

    print(allTitlesVisited)
    # Incrémentation du compteur de coups, si vous voulez tricher, retirez cette ligne
    counter = counter + counterIncrement


    # Génération et écriture dans le fichier html
    currentPath = os.path.dirname(__file__)
    currentPath = os.path.join(currentPath,"wiki.html")
    f = open(currentPath,'w+', encoding='utf-8')

    writeBeginningHtml(f, currentTitle, counter, descdescriptionFinal)
    if len(allLinksVisited) > 1:
        writeGoBackhtml(f)
    writeEndHtml(f, allGoodLinksUnique, allGoodLinksUrl, allGoodLinksTitre)

    # Recharge la page quand on clique sur un lien
    if not firstLoad:
        eel.reloadPage()
    else:
        firstLoad = False

    # Remet les valeurs de ces deux variables de base
    counterIncrement = 1
    addTab = True

    print("\n")

#! FONCTION DE DÉPART
# Fonction d'initialisation, ouvre la page wiki,
# et lance la fonction pour savoir si le joueur a gagné ou non
@eel.expose
def initiate(Linkurl):
    global currentPage
    currentPage = openPage(Linkurl)

    global currentTitle
    checkEndGame(currentTitle)

#--------------------------------------------
# Initialisation du code
#--------------------------------------------

# Initialisation de la borne et le titre de début, et de fin
firstBorne, firstBorneUrl = getBorne()
lastBorne, lastBorneUrl = getBorne()

#! (TRICHE)
# Si vous voulez tricher, vous pouvez mettre des valeurs manuelles qui remplaceront les bornes
# (AUCUNE VERIFICATION N'EST FAITE SUR CE QUE VOUS ÉCRIVEREZ)
#TODO : Possiblité de choisir ses bornes directement dans l'interface (Prévu pour la v3, qui sortira peutêtreunjourjesaispasj'aitropdeprojets)

"""
firstBorne = "Gnocchi"
firstBorneUrl = "Gnocchi"
lastBorne = "Grenoble"
lastBorneURL = "Grenoble"
"""


print("{} > {}".format(firstBorne, lastBorne))

# Lancement de la fonction d'initialisation
initiate(firstBorneUrl)

# Lancement d'eel
eel.start('wiki.html', mode="chrome-app")
