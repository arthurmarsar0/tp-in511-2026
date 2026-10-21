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