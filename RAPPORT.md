# Rapport TP Agents IA

Binôme : ALVES MARSARO Arthur & ROCHA GOMES Marcos Vinicius

## Exercices

### Exercice 1.1 — Découverte du tool calling

**1. Est-ce que l'analyse dans `reasoning_content` est correcte ?**

Oui, l'analyse est correcte. Le LLM identifie la demande de l'utilisateur comme une multiplication de 15 par 8. Il reconnaît que l'outil `Calculator` est adapté à cette opération et génère les arguments nécessaires : `operation = "multiply"`, `a = 15` et `b = 8`.

**2. Que contient le champ `tool_calls` dans la réponse du LLM ?**

Le champ `tool_calls` contient une liste des appels d'outils demandés par le LLM. Dans notre cas, il contient un appel à `Calculator`, avec le nom de la fonction, ses arguments au format JSON et un identifiant unique (`id`) permettant d'associer l'appel à son résultat.

**3. Pourquoi le LLM a-t-il choisi d'appeler `Calculator` plutôt que de répondre directement ?**

Le LLM a choisi `Calculator` parce que cet outil était disponible et correspondait à l'opération demandée. L'utilisation d'un outil spécialisé permet de déléguer le calcul à une fonction Python, ce qui peut améliorer la fiabilité du résultat.

**4. Que se passe-t-il si vous ne passez pas l'argument `tools` à `call_llm` ?**

Sans l'argument `tools`, le LLM ne reçoit pas la description des outils disponibles. Il doit donc répondre directement à partir de ses propres capacités, sans demander l'exécution de `Calculator`. Pour cette opération simple, il pourrait répondre directement « 120 ».

### Exercice 1.2 — Exécuter l'outil appelé

**Pourquoi faut-il ajouter la réponse du LLM (`message`) avant le résultat de l'outil ?**

*The language model dont have any statement and dont utilizes remainder memory between two calls of the llm. Knowing this behaviour, the model resent the "internql conversation" as some feature to depart, so it has some refinement on the answer*

**Quel est le rôle du champ `tool_call_id` ?**

*Associate each call to its operation by an unique string, thats important to keep track of the processus of the LLM to get to the answer*

**Que se passe-t-il si vous oubliez d'ajouter le résultat de l'outil à l'historique ?**

*The LLM will ever not read the answer, that means that probabably it will either create an answer or remake that same call*

### Exercice 1.3 - Définir votre propre outil

**Comment le LLM sait-il quels sont les paramètres de l'outil ?**

Because of the function `make_tool`, that inside of it has also `to_openai_tool` that makes the converstion needed to the LLM be able to understand. Basically changes to a schema JSON informing the parametres, its type and "nullability".

**2. Que se passe-t-il si vous ajoutez un champ avec une valeur par défaut ?**

Si un champ possède une valeur par défaut, il devient généralement optionnel dans le schéma JSON. Le LLM peut donc appeler l'outil sans fournir ce paramètre. Dans ce cas, Python utilise automatiquement la valeur définie par défaut lors de l'instanciation de la dataclass.

**3. Pouvez-vous ajouter un champ `Literal["french", "english"]` pour restreindre les valeurs possibles ?**

Oui, il est possible d'utiliser `Literal` du module `typing` pour limiter les valeurs autorisées dans le schéma JSON. Par exemple, un champ `language: Literal["french", "english"]` permet d'indiquer au LLM que seules ces deux valeurs sont acceptées. Cependant, cette annotation ne garantit pas à elle seule une validation des valeurs à l'exécution.

### Exercice 2.1 - La boucle complète

### Exercice 2.2 - Créer un agent SQL

Nous avons repris la boucle de l'exercice 2.1, mais avec les outils SQL (`SQLQuery`, `ListTables`, `DescribeTable`) créés par `make_sql_tools(db)` au lieu de `Calculator`. La boucle est limitée à 5 itérations par question.

En général, le LLM commence par `ListTables` ou `DescribeTable` pour voir la structure de la base, puis il écrit la requête avec `SQLQuery`. Le résultat de chaque outil est ajouté à l'historique avec le rôle `"tool"`, et le LLM s'en sert pour donner la réponse finale.

### Exercice 2.3 - Améliorer le system prompt

**Quelle variante produit les meilleures réponses ?**

La variante A (JOINs) donne les meilleures réponses pour les questions qui utilisent plusieurs tables, parce que le LLM fait une seule requête au lieu de plusieurs. La variante B est utile quand une requête échoue, parce que le LLM corrige la requête au lieu de s'arrêter.

**Le prompt influence-t-il le nombre d'itérations ?**

Oui. Avec la variante A, le LLM fait moins d'appels car il regroupe les informations dans une seule requête. Avec la variante C, il explique avant chaque appel, ce qui donne des réponses plus grands.

**Peut-on demander au LLM de "penser étape par étape" (chain-of-thought) ?**

Oui. Le LLM explore d'abord le schéma étape par étape puis écrit la requête. Comme le modèle raisonne déjà dans le champ reasoning_content, l'effet est moins visible, mais ça l'aide à suivre un ordre logique.


## Difficultés rencontrées


### Choix d'utilisation des outils par le LLM (Partie 1)

Lors des exercices 1.1 et 1.2, nous avons observé que le LLM n'utilise pas systématiquement les outils mis à sa disposition.

Par exemple, lorsque nous lui avons demandé de calculer `10!`, il a répondu directement sans faire appel à `Calculator`. En revanche, lorsque nous avons reformulé la même opération sous la forme `10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1`, il a commencé à effectuer les multiplications successives avec l'outil, jusqu'à atteindre la limite d'itérations.

Cette expérience nous a permis de comprendre que le choix d'utiliser un outil dépend de l'interprétation de la requête par le modèle. La simple disponibilité d'un outil ne garantit donc pas son utilisation, sauf si son usage est explicitement imposé et respecté par le modèle.

Nous avons également constaté que la formulation d'une question peut influencer le nombre d'appels d'outils nécessaires et, par conséquent, la capacité de l'agent à terminer une tâche dans la limite d'itérations définie.


### Compatibilité de l'environnement avec macOS

Une autre difficulté rencontrée concernait l'installation des dépendances et l'exécution du projet sous macOS.

Le `Makefile` fourni était principalement conçu pour un environnement Linux (Ubuntu/Debian), utilisant notamment `apt-get` pour installer les dépendances. Or, cette commande n'est pas disponible sous macOS, ce qui empêchait l'exécution de `make setup`.

Pour résoudre ce problème, nous avons utilisé Homebrew pour installer les dépendances nécessaires, puis exécuté séparément les différentes étapes de configuration (`make pyenv`, `make pull`, `make model` et `make template`).

Nous avons également dû démarrer Docker Desktop afin de rendre le serveur `llama.cpp` accessible. Après ces adaptations, nous avons pu lancer le modèle et vérifier son fonctionnement grâce aux endpoints `/health` et `/v1/models`.

Cette difficulté nous a permis de mieux comprendre les différences entre les environnements Linux et macOS, ainsi que l'importance de la portabilité des scripts d'installation.

### Gestion du contexte

Une difficulté potentielle concerne la gestion du contexte lors des interactions avec le LLM. Certains systèmes utilisent des mécanismes de résumé pour réduire la taille de l'historique, ce qui peut entraîner la perte d'informations importantes, notamment les instructions initiales.

Une solution serait d'utiliser un résumé cumulatif, mis à jour progressivement, tout en conservant les consignes essentielles. Cela permettrait d'optimiser l'utilisation du contexte sans compromettre la cohérence des réponses.

## Démarche suivie

### Démarche suivie

Dans un premier temps, nous avons étudié le code fourni afin de comprendre son fonctionnement et les outils mis à notre disposition. Ensuite, nous avons adopté une approche progressive, en implémentant les fonctionnalités étape par étape et en effectuant des tests réguliers.

Cette démarche nous a permis de vérifier le bon fonctionnement de chaque étape et de comprendre en profondeur les mécanismes utilisés avant de passer à la suivante.

## Solutions apportées et résultats


### Exercice 2.1 — Tests de la boucle agent

Nous avons testé la boucle agent avec quatre opérations mathématiques afin de vérifier sa capacité à utiliser l'outil `Calculator` et à gérer plusieurs appels successifs.

| Question | Résultat attendu | Résultat obtenu | Itérations |
|---|---|---|---|
| How much is 10! ? please use the tool Calculator | 3 628 800 | Max iterations reached (Stopped in 151200) | 5 |
| What is 15 times 8? | 120 | Answer: The result of 15 times 8 is 120. | 2 |
| Calculate (12 + 8) * 3. | 60 | Answer: The result of (12 + 8) * 3 is 60. | 3 |
| What is 100 divided by 4, plus 10? | 35 | 35 | 3 |

**Observations :**

Dans tous les tests ayant abouti à une réponse finale, nous avons constaté que la dernière itération était consacrée à la formulation de la réponse, sans nouvel appel à l'outil `Calculator`.

Ainsi, le nombre d'itérations contenant des appels d'outils était égal au nombre total d'itérations moins une :

`N_itérations_avec_outils = N_itérations_totales - 1`

Cela montre qu'une itération supplémentaire est nécessaire pour que le LLM interprète les résultats des outils et génère sa réponse finale.

### Exercice 2.2 — Tests de l'agent SQL

Nous avons soumis cinq questions à l'agent SQL afin d'évaluer sa capacité à explorer la structure de la base de données, à générer des requêtes SQL et à interpréter les résultats obtenus.

| Question | Résultat obtenu |  Itérations |
|---|---|---|
| Books written after 1970 |The Dispossessed, Children of Dune, Kindred, Parable of the Sower, Neuromancer, Snow Crash, The Three-Body Problem | 4 |
| Author of 'Dune' and birth year | Max iterations reached | 5 |
| Number of books per genre | **Cyberpunk:** 2,  **Dystopian:** 4, **Fantasy:** 4, **Satire:** 1, **Science Fiction:** 13 | 4 |
| Average rating per publisher | **Ace Books**: 4.22, **Gollancz**: 4.3625, **HarperCollins**: 4.22, **Penguin Books**: 4.25,  **Tor Books**: 4.15 | 5 |
| Author with the most books | Answer: Ursula K. Le Guin has written the most books according to the database. | 5 |


## Réflexions

- Que pensez-vous du mécanisme de tool calling ?
- Quels sont les risques de sécurité d'un agent SQL ?
- Comment améliorer la gestion du contexte ?
- Quelles fonctionnalités vous sembleraient intéressantes d'ajouter ?