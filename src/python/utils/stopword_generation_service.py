from stopword_generator import StopWordGenerator

def stopword_handler(event, context):
    sw = StopWordGenerator()
    sw.generate_stopwords()
    sw.add_stopwords_table()
    tokens = sw.get_stop_words()
    return tokens
