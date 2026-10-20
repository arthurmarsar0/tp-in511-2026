# TP - Agents IA avec outils (tool calling)

## Objectifs

À l'issue de ce TP, vous serez capable de :

1. Mettre en oeuvre le mécanisme de "tool calling" des LLMs
2. Définir des outils sous forme de dataclasses Python et les exposer à un LLM
3. Comprendre les enjeux du contexte d'un agent
4. Implémenter une boucle agent
5. Ajouter des garde-fous

---

## Partie 1 - Découverte du tool calling

### Objectif

Comprendre comment un LLM peut appeler des fonctions (outils) externes, et manipuler ce mécanisme avec le package `utils`.

### Librairies

Le package `utils` contient les fonctions nécessaires :

```
utils/
├── __init__.py     # API publique (ce que vous importez)
├── llm.py          # Appels LLM, conversion JSON Schema
├── tools.py        # Database, outils SQL, Calculator [À LIRE]
└── data.py         # Création de la base de démo [À LIRE]
```

**Lecture recommandée avant de commencer** :

Avant de commencer les exercices, prenez 10 minutes pour lire :

1. `utils/data.py` - Comprendre comment la base de démo est créée (tables, données). Cela vous aidera à identifier les questions que vous pourrez poser à votre agent.

2. `utils/tools.py` - Comprendre :
   - La classe `Database` (méthodes `execute`, `list_tables`, `describe_table`)
   - La fonction `make_sql_tools(db)` qui crée les 3 outils SQL
   - La dataclass `Calculator` (exemple simple d'outil)

> **Note** : `utils/llm.py` contient la logique de communication avec le LLM (appels HTTP, conversion JSON Schema). Vous n'avez pas besoin de lire ce fichier en détail pour ce TP.

---

### Primitives essentielles à maîtriser

Avant de commencer, assurez-vous de comprendre ces concepts clefs :

#### 1. Le registre (`registry`)

Le **registre** est un dictionnaire qui fait correspondre le **nom d'un outil** (le texte) vers sa **classe Python** (un objet python):

```python
# texte vu par le LLM => classe Python
registry = {
    "Calculator": Calculator,
    "SQLQuery": SQLQuery,
    "ListTables": ListTables,
}
```

Quand le LLM décide d'appeler un outil, il renvoie le **nom** de l'outil (ex: `"Calculator"`). Le registre permet de retrouver la classe Python correspondante pour l'instancier et l'exécuter.

C'est à vous de créer ce dictionnaire avec la fonction `make_registry` (dans llm.py) en utilisant la liste des outils à présenter au LLM. Par exemple :

```python
registry = make_registry([Calculator, SQLQuery])

# renvoie dans registry le dictionnaire suivant:
# registry = {
#    "Calculator": Calculator,
#    "SQLQuery": SQLQuery,
#}
```

#### 2. `execute_tool(tool_call, registry)`

Cette fonction fait le lien entre la demande du LLM et l'exécution réelle :

```python
# Le LLM a renvoyé ceci:
tool_call = {
    "id": "call_abc123",
    "function": {
        # Nom de l'outil
        "name": "Calculator",

        # Arguments en JSON string
        "arguments": '{"operation": "multiply", "a": 15, "b": 8}'
    }
}

# execute_tool fait:
# 1. Retrouve la classe "Calculator" dans le registry
# 2. Parse les arguments JSON -> {"operation": "multiply", "a": 15, "b": 8}
# 3. Instancie: Calculator(operation="multiply", a=15, b=8)
# 4. Exécute: instance() -> appelle __call__() -> retourne 120
# 5. Retourne le résultat en string JSON: '{"result": 120}'
result = execute_tool(tool_call, registry)
```

#### 3. `make_tools(tool_classes)`

Convertit une liste de **classes** (dataclasses) en **schémas JSON** (pour présenter les informations au LLM) :

```python
tools = make_tools([Calculator, SQLQuery])
# [
#   {"type": "function", "function": {"name": "Calculator", "description": "...", "parameters": {...}}},
#   {"type": "function", "function": {"name": "SQLQuery", "description": "...", "parameters": {...}}}
# ]
```

Ce schéma est envoyé au LLM pour qu'il sache quels outils sont disponibles et quels paramètres ils prennent.

#### 4. Le flow complet

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Dataclass  │────▶│ make_tools  │────▶│  call_llm   │────▶│    LLM      │
│  (outil)    │     │  (schema)   │     │  (avec      │     │  (décide    │
│             │     │             │     │   tools)    │     │   quel outil│
└─────────────┘     └─────────────┘     └─────────────┘     │   appeler)  │
                                                            └──────┬──────┘
                                                                   │
                              ┌─────────────┐     ┌─────────────┐  │
                              │ execute_tool│◀────│  registry   │◀─┘
                              │  (exécute)  │     │ (nom->class)│
                              └──────┬──────┘     └─────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   Résultat  │
                              │  (JSON str) │
                              └─────────────┘
```

---

**Base de données de démo** :

| Table | Colonnes | Lignes |
|-------|----------|--------|
| `authors` | id, name, birth_year, nationality | 12 |
| `publishers` | id, name, founded_year, country | 7 |
| `books` | id, title, author_id, publisher_id, year, genre, pages, rating | 24 |

---

### Exercice 1.1

Créez un fichier `exercice_1_1.py` avec un outil `Calculator` (déjà fourni dans `utils`) et testez-le.

**Consigne** :

1. Importez `Calculator`, `make_tools`, `make_registry`, `call_llm` depuis `utils`
2. Créez les outils et le registre
3. Affichez le schéma JSON de l'outil `Calculator`
4. Envoyez une requête au LLM avec cet outil : *"What is 15 times 8?"*
5. Vérifiez que le LLM appelle bien l'outil `Calculator`

> **Indice** : Utilisez `make_tools()` pour convertir la dataclass en schéma JSON, puis `call_llm(messages, tools=tools)` pour envoyer la requête.

**Questions de réflexion** :

- Est-ce que l'analyse dans `reasoning_content` est correcte ?
- Que contient le champ `tool_calls` dans la réponse du LLM ?
- Pourquoi le LLM a-t-il choisi d'appeler `Calculator` plutôt que de répondre directement ?
- Que se passe-t-il si vous ne passez pas l'argument `tools` à `call_llm` ?

Répondre dans votre rapport de TP.

---

### Exercice 1.2 - Exécuter l'outil appelé

Le LLM demande d'appeler un outil, mais c'est à vous de l'exécuter.

Créez un fichier `exercice_1_2.py`.

**Consigne** :

1. Utilisez `execute_tool(tool_call, registry)` pour exécuter l'outil appelé
2. Ajoutez le résultat à l'historique des messages avec le rôle `"tool"`
3. Faites un deuxième appel au LLM avec le résultat pour obtenir la réponse finale

> **Indice** : N'oubliez pas d'ajouter la réponse du LLM (`message`) à l'historique **avant** le résultat de l'outil.

**Questions de réflexion** :

- Pourquoi faut-il ajouter la réponse du LLM (`message`) avant le résultat de l'outil ?
- Quel est le rôle du champ `tool_call_id` ?
- Que se passe-t-il si vous oubliez d'ajouter le résultat de l'outil à l'historique ?

Répondre dans votre rapport de TP.

---

### Exercice 1.3 - Définir votre propre outil

Créez un fichier `exercice_1_3.py` contenant un nouvel outil `WordCounter` qui compte le nombre de mots dans un texte.

**Consigne** :

1. Créez une dataclass `WordCounter` avec :
   - Un champ `text: str`
   - Une méthode `__call__()` qui retourne le nombre de mots
   - Un docstring décrivant l'outil (sera utilisé comme description pour le LLM)
2. Testez-le avec le LLM : *"How many words are in 'Hello world, this is a test'?"*

> **Indice** : Une dataclass outil doit avoir un docstring (description pour le LLM), des champs (paramètres), et une méthode `__call__()` (exécution). Utilisez `len(self.text.split())` pour compter les mots.

**Questions de réflexion** :

- Comment le LLM sait-il quels sont les paramètres de l'outil ?
- Que se passe-t-il si vous ajoutez un champ avec une valeur par défaut ?
- Pouvez-vous ajouter un champ `Literal["french", "english"]` pour restreindre les valeurs possibles ?

Répondre dans votre rapport de TP.

---

## Partie 2 - La boucle agent

### Objectif

Implémenter la boucle complète : LLM → outils → LLM → réponse, avec gestion des itérations.

### Schéma de la boucle

```
┌─────────────────┐
│  Question       │
│  utilisateur    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  messages = [system_prompt, user]       │
│  pour i dans range(max_iterations):     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
         ┌─────────────────┐
    ┌───▶│   call_llm()    │
    │    │  (messages +    │
    │    │     tools)      │
    │    └────────┬────────┘
    │             │
    │             ▼
    │    ┌─────────────────┐
    │    │  Ajouter réponse│
    │    │  LLM à messages │
    │    └────────┬────────┘
    │             │
    │             ▼
    │    ┌─────────────────┐     NON      ┌─────────────┐
    │    │  Des tool_calls │─────────────▶│  Retourner  │
    │    │    présents ?   │              │   réponse   │
    │    └────────┬────────┘              │   finale    │
    │             │ OUI                   └─────────────┘
    │             ▼
    │    ┌─────────────────┐
    │    │  Pour chaque    │
    │    │  tool_call:     │
    │    │  execute_tool() │
    │    └────────┬────────┘
    │             │
    │             ▼
    │    ┌─────────────────┐
    │    │  Ajouter le     │
    │    │  résultat à     │
    │    │  messages       │
    │    │  (rôle "tool")  │
    │    └────────┬────────┘
    │             │
    └─────────────┘
```

### Exercice 2.1 - La boucle complète

Implémentez la boucle agent avec le seul outil `Calculator`.

**Algorithme** :

```
1. Créer la liste des messages (system prompt + question utilisateur)
2. Tant que (nombre d'itérations < max_iterations):
   a. Appeler le LLM avec les messages et les outils
   b. Ajouter la réponse du LLM à l'historique
   c. Si la réponse ne contient pas de tool_calls:
      → Retourner le contenu (réponse finale)
   d. Sinon, pour chaque tool_call:
      → Exécuter l'outil avec execute_tool()
      → Ajouter le résultat à l'historique (rôle "tool")
3. Retourner "Max iterations reached"
```

Tester votre agent avec des requêtes de calculs et mettez à jour votre rapport de TP avec les résultats obtenus.

---

### Exercice 2.2 - Créer un agent SQL

Créez le fichier `sqlite_agent.py` à la racine du projet avec :

1. Les imports depuis `utils`
2. La boucle agent complète
3. Un bloc `__main__` qui :
   - Crée la base de données (`Database("library.db")`)
   - Crée les outils SQL (`make_sql_tools(db)`)
   - Pose 5 questions de test

**Questions de test** :

```python
questions = [
    "What are the books written after 1970?",
    "Who is the author of 'Dune' and when were they born?",
    "How many books are there per genre?",
    "What is the average rating per publisher?",
    "Which author has written the most books?",
]
```

**Vérification** :

Votre agent doit :

- [ ] Répondre correctement aux 5 questions
- [ ] Utiliser les outils SQL (`SQLQuery`, `ListTables`, `DescribeTable`)
- [ ] Ne pas dépasser 5 itérations par question
- [ ] Gérer les appels d'outils (exécuter et renvoyer le résultat au LLM)

Intégrer le code (commenté) dans votre rapport de TP en annexe.

---

### Exercice 2.3 - Améliorer le system prompt

Le `system_prompt` influence fortement le comportement du LLM. Expérimentez avec différentes versions.

**Version de base** :

```python
SYSTEM_PROMPT = """You are a SQL assistant with access to a SQLite database.

Tools:
- ListTables: list all tables
- DescribeTable: get table structure
- SQLQuery: execute any SQL query

Think step by step. Explore the schema first, then query."""
```

**Consigne** :

Testez au moins 2 variantes et comparez les résultats :

- Variante A : Ajouter *"Always use JOINs instead of multiple queries when possible."*
- Variante B : Ajouter *"If a query fails, analyze the error and try again with a corrected query."*
- Variante C : Ajouter *"Explain your reasoning before each tool call."*

**Questions de réflexion** :

- Quelle variante produit les meilleures réponses ?
- Le prompt influence-t-il le nombre d'itérations ?
- Peut-on demander au LLM de "penser étape par étape" (chain-of-thought) ?

Répondre dans votre rapport de TP.

---

## Partie 3 - Extensions (optionnel)

Choisissez **au moins une** extension à implémenter.

### Extension A - Guardrails de sécurité

Sécurisez votre agent contre les requêtes dangereuses.

**Consigne** :

1. Modifiez la classe `Database` dans `utils/tools.py` (ou créez une sous-classe) pour :
   - Ouvrir la BDD en mode read-only (`sqlite3.connect(f"file:{path}?mode=ro", uri=True)`)
   - Bloquer les mots-clés dangereux : `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`
   - N'autoriser que les requêtes `SELECT` et `WITH`

**Questions de réflexion** :

- Pourquoi le mode read-only ne suffit-il pas ?
- Comment un attaquant pourrait-il contourner un blocage par mots-clés ?
- Existe-t-il des bibliothèques pour parser et valider du SQL ?

---

### Extension B - Gestion des erreurs SQL

Quand le LLM génère une requête SQL invalide, l'agent doit pouvoir réessayer.

**Consigne** :

1. Dans la boucle agent, si `execute_tool` retourne une erreur SQL :
   - Le résultat contient `{"error": "..."}`
   - Le LLM voit cette erreur et peut réessayer avec une requête corrigée
2. Ajoutez un compteur d'erreurs : si 3 erreurs consécutives, abandonner

**Questions de réflexion** :

- Le LLM comprend-il bien les messages d'erreur SQLite ?
- Faut-il reformuler l'erreur pour aider le LLM ?

---

### Extension C - Nouveaux outils

Ajoutez un nouvel outil à votre agent. Exemples :

- `SearchBooks(keyword: str)` : recherche des livres par mot-clé dans le titre
- `GetAuthorBooks(author_name: str)` : liste les livres d'un auteur
- `AddBook(title, author, year)` : ajoute un livre (mode write !)

---

### Extension D - Multi-agents

Créez deux agents spécialisés qui collaborent :

- **Agent 1 (Planner)** : analyse la question et produit un plan
- **Agent 2 (Executor)** : exécute le plan avec les outils SQL

---

## Rendu

Vous devez rendre :

| Fichier | Description |
|---------|-------------|
| `sqlite_agent.py` | Votre agent complet (boucle + `__main__`) |
| `exercice_1_1.py` | Exercice 1.1 (premier outil) |
| `exercice_1_2.py` | Exercice 1.2 (exécution d'outil) |
| `exercice_1_3.py` | Exercice 1.3 (outil personnalisé) - optionnel |
| `RAPPORT.md` | 1 page : difficultés rencontrées, solutions, réflexions |

**Format du rapport** :

```markdown
# Rapport TP Agents IA

Binôme : ...

## Exercices

...

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

```

---

## Ressources

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [OWASP - LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## ❓ FAQ

**Q: Le LLM ne voit pas mes outils, que faire ?**
R: Vérifiez que vous passez bien `tools=tools` à `call_llm()`. Vérifiez aussi que le schéma JSON est valide.

**Q: Le LLM génère du SQL invalide, que faire ?**
R: Ajoutez des exemples dans le `system_prompt`. Implémentez la gestion d'erreurs (Extension B).

**Q: Mon contexte dépasse la limite du modèle, que faire ?**
R: Limitez le nombre d'itérations (`max_iterations=5`). Supprimez les résultats d'outils trop longs de l'historique. Ou implémentez une classe `Agent` avec une méthode `reset()` pour réinitialiser le contexte.

**Q: Puis-je utiliser d'autres bibliothèques Python ?**
R: Oui, mais demandez d'abord à l'enseignant. Le TP est conçu pour fonctionner avec `msgspec` et `requests` uniquement.
