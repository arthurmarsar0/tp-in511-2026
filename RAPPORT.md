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

### Exercice 2.3 - Améliorer le system prompt


**Quelle variante produit les meilleures réponses ?**

**Le prompt influence-t-il le nombre d'itérations ?**

**Peut-on demander au LLM de "penser étape par étape" (chain-of-thought) ?**


## Difficultés rencontrées

- ...

## Démarche suivie

- ...

## Solutions apportées et résultats

- ...

## Réflexions

- Que pensez-vous du mécanisme de tool calling ?
- Quels sont les risques de sécurité d'un agent SQL ?
- Comment améliorer la gestion du contexte ?
- Quelles fonctionnalités vous sembleraient intéressantes d'ajouter ?