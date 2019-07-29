# Mapping to three standard wikidata classes: ORG, PER, LOC
# https://github.com/explosion/spaCy/blob/719a15f23d76f219fd303e94a8384c50c9fd61e2/spacy/glossary.py#L282-L309
ONTONOTES_TO_WIKIPEDIA_LABEL_MAPPING = {
  "PERSON": "PER", # "People, including fictional",
  "NORP": "ORG", # "Nationalities or religious or political groups",
  "FACILITY": "LOC", # "Buildings, airports, highways, bridges, etc.",
  "FAC": "LOC", # "Buildings, airports, highways, bridges, etc.",
  "ORG": "ORG", # "Companies, agencies, institutions, etc.",
  "GPE": "LOC", # "Countries, cities, states",
  "LOC": "LOC", # "Non-GPE locations, mountain ranges, bodies of water",
  # "PRODUCT": "Objects, vehicles, foods, etc. (not services)",
  # "EVENT": "Named hurricanes, battles, wars, sports events, etc.",
  # "WORK_OF_ART": "Titles of books, songs, etc.",
  # "LAW": "Named documents made into laws.",
  # "LANGUAGE": "Any named language",
  # "DATE": "Absolute or relative dates or periods",
  # "TIME": "Times smaller than a day",
  # "PERCENT": 'Percentage, including "%"',
  # "MONEY": "Monetary values, including unit",
  # "QUANTITY": "Measurements, as of weight or distance",
  # "ORDINAL": '"first", "second", etc.',
  # "CARDINAL": "Numerals that do not fall under another type",
  # Named Entity Recognition
  # Wikipedia
  # http://www.sciencedirect.com/science/article/pii/S0004370212000276
  # https://pdfs.semanticscholar.org/5744/578cc243d92287f47448870bb426c66cc941.pdf
  "PER": "PER", # "Named person or family.",
  # "MISC": "Miscellaneous entities, e.g. events, nationalities, products or works of art",
}
