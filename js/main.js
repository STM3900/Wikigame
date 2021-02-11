//C'est ici que sont les fonctions qui seront utilisées plus tard dans nos scripts

//Selecteurs
const hideLinks = document.querySelector(".wiki-links");
const loading = document.querySelector(".loading");

//Fonction d'animation
const hideLinksFunction = () => {
  hideLinks.classList.add("hide");
  loading.style.animationPlayState = "running";
  loading.classList.remove("hide");
};

//fonctions python > js
const nextPage = (url) => {
  hideLinksFunction();
  eel.initiate(url);
};

const goBackJS = (url) => {
  hideLinksFunction();
  eel.initiate(url);
};
