import pymorphy2


def get_collections(raw_collections):
    collections = list()
    for collection in raw_collections:
        words = []
        for word in collection.word:
            words.append(word.word)
        morph = pymorphy2.MorphAnalyzer()
        slov_parse = morph.parse('слово')[0]
        slov = slov_parse.make_agree_with_number(len(words)).word
        collections.append({'name': collection.name,
                            'description': collection.description,
                            'image': ''.join(['../', str(collection.image)]),
                            'words_len': ' '.join((str(len(words)), slov)),
                            'words': words,
                            'id': collection.id})
    return collections