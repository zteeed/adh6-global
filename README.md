

# ADH6
Auteur original: *Nicolas Bonnet*

Liste des contributeurs:
* Aurélien Duboc

## Notes
Je vous invite **vivement** à aller lire [la page sur le wiki](https://wiki.minet.net/wiki/services/adh6) avant de vous plonger dans l'exploration de ce repo.

Si vous voyez une modification à apporter (correction de faute, éclaircissement d'un point, ajout d'instructions supplémentaire, mise à jour d'anciennes information, etc.) **n'hésitez pas à faire un commit et à vous ajouter dans la liste des contributeurs**. Toute aide est la bienvenue !

## Présentation
ADH est le système de gestion d'adhérent de l'association [MiNET](https://minet.net). Ce document a pour but de présenter la sixième version de notre outil.
## Motivations
Nous voulons produire un outil de gestion des adhérent **simple à maintenir**. Pour cela, nous prônons la *simplicité* dans *toutes* les parties de notre projet. Le but est de créer un outil maintenable, qui effectue **sa mission et qui l'a fait bien**.

Pour cela nous avons décidé de **dissocier le backend du frontend**. Ainsi un changement d'interface ne nous obligera pas à réécrire toute la logique du code (comme c'est le cas avec la précédente version).

Pour atteindre ses objectifs, nous essayons de **réduire le boilerplate code** en utilisant des bibliothèques qui sont *réputées et prouvées stables*. Cela permettra d'avoir moins de lignes de code, plus de *readability* et donc moins de potentiel bug.

La **fiabilité** de notre outil est aussi un concept important à nos yeux. C'est pour cela que nous faisons beaucoup appels à des **tests d'intégration** (*200+ pour la partie backend pour l'instant*). Nous visons un taux de *code coverage* le plus haut possible.

## Comment contribuer ?

Allez sur gitlab.minet.net sur [la page du projet](https://gitlab.minet.net/adh6/core/). Si vous n'avez pas les accès, n'hésitez pas à les demander à zTeeed ou InsolentBacon (vous pouvez les contacter tous les deux dans la vraie vie ou sur mattermost/IRC). Une fois que vous y êtes, allez voir dans les issues, trouvez une qui vous plaît et assignez la vous! N'hésitez pas à demander des précisions sur les issues (aux deux mêmes zigotos), nous nous ferons un plaisir de tout vous expliquer!

## Choix des technos
### Communication client/serveur

Pour communiquer entre le client et le serveur, nous avons décidé d'utiliser une API.
En terme de techno, on a décidé de prendre la techno la plus stable et universelle (compatible avec tous les futurs projets), HTTP.

Nous avons décidé de ne pas reprogrammer à la main tout un client/serveur pour notre API. Ca aurait était faisable, mais trop error-prone et on risque de perdre en flexibilité (un changement dans l'API devrait être réfléchi dans le code du client ET du serveur). Nous avons donc décidé d'utiliser un système de "generation" de code automatique à partir d'une spec.

Pour définir la specification de notre API nous utilisons OpenAPI (aussi appelé swagger, oui, oui...).

Pour générer le code serveur, on utilise d'un côté connexion, qui est une libary python développée par Zalando. https://github.com/zalando/connexion Allez voir le repo, il est assez actif. C'est aussi la bibliothèque de génération de code prise comme référence par Swagger (l'organisme qui fait OpenAPI).

Pour le côté client, on utilise directement swagger-codegen, édité directement par Swagger. https://github.com/swagger-api/swagger-codegen Pareil, allez voir leur repo, il est "assez" actif... (10 228 commits à l'heure où j'écris ces lignes, et plus de 900 contributeurs...)
Ca semble donc aussi être un assez bon choix pour produire un code stable.

En résumé, on a pris le parti prix d'ajouter deux dépendances au projet, mais on a gagné en flexibilité et en maintenabilité.


## Backend

### Le choix des technos

### How to setup the project
- Create a virtualenv ```virtualenv ./```
- Enter the virtualenv ```source bin/activate```
- Install the requirements ```pip3 install -r requirements.txt```
- Fill the setting file ``` cp CONFIGURATION.py{.example,} && vim CONFIGURATION.py ``` 
- Install the UWSGI server ``` apt install uwsgi uwsgi-plugin-python3 ```
- You can use the example configuration file provided for the UWSGI configuration ``` cp adh6-api.ini /etc/uwsgi/sites-available ```
- Activate the site``` ln -s /etc/uwsgi/sites-available /etc/uwsgi/sites-enabled ```
- Restart UWSGI ``` systemctl restart uwsgi ```

A UWSGI server is now running on your machine. To access the API, install a webserver (such as NGINX) and configure it to use the UWSGI server.

Note: this is not the easiest way to develop. Do not hesitate to ask an access of the test VMs. The whole environment is already setup.

###  Je suis perdu, qu'est-ce que c'est que tous ces dossiers ?
Ce projet consiste juste en l'implémentation des différents méthodes définies dans la spécification de l'API. 

Si vous êtes un PGM et que vous voulez juste lire le code, sachez juste que tout le code est dans le dossier *adh/*.

Pour que python se comporte en serveur Web on utilise *Flask*, et pour pas avoir à faire de trucs compliqués on utilise *connexion* qui fait le binding entre *Flask* et les fonctions en python qui sont appelées presque magiquement.

La spécification de l'API est stockée dans swagger.yaml à la racine du projet,
ce fichier est automatiquement exporté de swaggerhub.
https://app.swaggerhub.com/apis/insolentbacon/adherents/
** Si vous voulez modifier l'API, ne modifiez pas sur ce site (de toute façon vous n'aurez sûrement pas les droits), modifiez le fichier openapi/spec.yaml.** 
Le site permet just d'avoir une jolie représentation de l'API.

*En gros*, les fonctions importantes sont juste celles dans *adh/controller/*, 
qui sont appelées quand on fait des requêtes vers le serveur web.

Maintenant, parce qu'on veut pas faire de requêtes directement dans la BDD SQL (pour des raisons de sécurité et de flemme), on utilise *SQLAlchemy*. C'est en fait une bibliothèque qui permet de manipuler des objets dans la BDD comme des objets python (allez chercher ce qu'est un *ORM*).

En résumé on a:

- **controller/**: Le plus important, c'est là où sont les fonctions qui sont
appelées lorsque une requête HTTP est effectuée sur l'API.
- **model/**: C'est là où on définit ce qu'il y a dans la base de données (c'est
à dire les noms des tables, des colonnes, les contraintes qu'il y a sur les
champs [genre une IP doit être valide]). On importe ensuite les modèles dans les controllers pour manipuler la BDD
- **exceptions/**: c'est là où on met les erreurs custom qu'on a défini, c'est
peu important
- **test/**: c'est là où il y a des les tests. C'est super important. On teste
chacune des lignes de code des fichiers .py (on vise un *code coverage* de 95%)
Les cas normaux et extrêmes doivent être testés. C'est ce qui est executé
lorsque on lance pytest.

### Notes au futurs devs:
#### Comment lancer les tests ?
Lancez ```pytest``` dans la console, ou utilisez votre IDE... 

#### Comment obtenir une analyse du "code coverage" ?
```pytest --cov=adh --cov-report html``` dans la console.

#### A propos des sessions d'SQLAlchemy...
Quand vous implémentez une fonction de l'API dans controller, ne faites qu'UNE session SQLAlchemy, créée DANS votre fonction de controller. Ca évite les nested transactions qui sont pas toujours supportées. (et c'est plus propre, moins error-prone)

*Extrait de la doc d'SQLALchemy:*
> As a general rule, keep the lifecycle of the session separate and external 
> from functions and objects that access and/or manipulate database data. 
> This will greatly help with achieving a predictable and consistent 
> transactional scope.

#### Petites fonctions utiles

J'ai défini quelques fonctions utiles dans les modèles des objets de la BDD.

- dict(obj) permet de retourner un dict du format de l'api
- Obj.from_dict(dict) permet de retourner un obj en utilisant un dict de l'API
- Obj.find(session, value) permet de retourner l'objet qui est associé par l'API

## Frontend - Angular

### Pour installer:
- Installez NodeJS ([voir le site](https://nodejs.org/en/download/)). (pas la version 10, celle LTS en dessous)
- ```sudo npm install --unsafe-perms -g @angular/cli@^6.0.0```
- ```npm install```
- Éditez éventuellement ```src/app/auth.config.ts``` si vous voulez changer le serveur d'authentification.
- ``` npm start ```

*NOTE: nous utilisons la version 6 d'Angular*
*NOTE2: Si vous trouver que c'est trop compliqué de configurer tout l'environnement de test, demandez à un des developpeurs un accès sur les machines virtuelles de test! Tout est déjà préparé dessus.*

## Authentication server
### Introduction
Ce serveur un est un serveur OAuth2 qui a été implémenté en python grâce à la bibliothèque Authlib. Il est voué à être remplacé par une solution de [SSO](https://en.wikipedia.org/wiki/Single_sign-on) qui serait plus adaptée (On pourrait utiliser OpenID Connect).

On utilise le flow *Implicit grant* d'OAuth2.


### Comment lancer ?
- Install required packages ```sudo apt install libpcre3 libpcre3-dev uwsgi uwsgi-plugin-python3```
- Create a virtualenv ```virtualenv ./```
- Enter the virtualenv ```source bin/activate```
- Install the requirements ```pip3 install -r requirements.txt```
- Fill the setting file ``` cp CONFIGURATION.py{.example,} && vim CONFIGURATION.py ``` 
- You can use the example configuration file provided for the UWSGI configuration ``` cp adh6-api.ini /etc/uwsgi/sites-available ```
- Activate the site``` ln -s /etc/uwsgi/sites-available /etc/uwsgi/sites-enabled ```
- Restart UWSGI ``` systemctl restart uwsgi ```


