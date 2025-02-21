from random import choice
import gensim.downloader as api
from pymystem3 import Mystem
import string
from load_config import *
from typing import Dict
model = api.load("word2vec-ruscorpora-300")


def get_lemma(word):
  mystem = Mystem()
  lemma = mystem.lemmatize(word)[0]
  return lemma


def select_random_word():
  item = choice(list(model.key_to_index.items())[:load_config()["difficulty"]])
  return item[0].split("_")[0]



def get_most_similar_dict(word, topn):
  d = {k.split("_")[0]: k for k in model.key_to_index}
  vals = model.most_similar(d[word], topn=topn)
  d_ = {
      k.split("_")[0]: i + 2
      for i, (k, v) in enumerate(vals) if ":" not in k
  }
  return d_


def get_placement(word,word_dict):
  lemma = get_lemma(word)
  if lemma in word_dict:
    return word_dict[lemma]
  return -1

def init():
  init_word = select_random_word()
  non_english_chars = 0
  while non_english_chars != len(init_word):
    for char in init_word:
      if (char in string.ascii_lowercase) or (char in string.punctuation and char != "-"):
        init_word = select_random_word()
        break
      else: non_english_chars +=1
    

  word_dict = get_most_similar_dict(init_word, 184973)
  return (init_word,word_dict)

def get_string_words(similarities,top_num: int):
  end_string = f"<b>Топ-{top_num} слов:</b>\n\n"
  for i,(sim,count) in enumerate(similarities,1):
    if i <= top_num:
        end_string+=f"<i>{i}. {sim}</i> - <b>{count}</b>\n"
    else: break
  return end_string

def word_hint(word_dict: Dict[str,int],word: str, top: int = 100):
  word = choice(list(word_dict.items())[:top])
  return {
    "word": word,
    "text": f"<b>Вы использовали 💡Подсказку.\n\n{word[0]} - {word[1]}</b>"
  }