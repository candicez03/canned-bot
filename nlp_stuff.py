import random

import spacy
from benepar.spacy_plugin import BeneparComponent

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(BeneparComponent("benepar_en2"))


def walk_tree(t, depth=0):
    if len(t._.labels) > 0:
        print(f"{'  '*depth}{t._.labels[0]}: {str(t)}, lemma: {t.lemma_}")
        if any(x in t._.labels[0] for x in('VP', 'NP', 'ADJ')):
            possibleReplies.append(t.lemma_)
    else:
        print(f"{'  '*depth}{t[0].pos_} ({t[0].tag_}): {str(t)}, lemma: {t.lemma_}")
    for child in list(t._.children):
        walk_tree(child, depth+1)


def getReply(message, emoji_freq=50):
    doc = nlp(message)
    reply = ''
    return reply


print('ready')
while True:
    possibleReplies = list()
    message = list(nlp(input()).sents)
    [walk_tree(part) for part in message]
    print(possibleReplies)
