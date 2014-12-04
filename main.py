# -*- coding: utf-8 -*-

from synonymizer import Synonymizer
import pymorphy2
import codecs
import nltk
import string

def make_text_clear(text_in, synonymizer, morph):
	sentences = nltk.PunktSentenceTokenizer().tokenize(text_in.lower())
	text_items_in = []
	for sentence in sentences:
		for word in nltk.WordPunctTokenizer().tokenize(sentence):
			text_items_in.append(word)
	text_out = u''
	punct = set(string.punctuation)
	for item in text_items_in:
		if item not in punct:
			word_info = morph.parse(item)[0]
			norm = word_info.normal_form	
			synonyms = synonymizer.synonymize(norm)
			print "-----------------"
			print("Word: %s" % norm)
			print("Synonyms:")
			for syn, freq in synonyms:
				print("%s : %s" % (syn, freq))
			print "-----------------"
			if len(synonyms) is not 0:
				best_synonym = synonyms[0][0]
				if synonymizer.need_replace(norm,best_synonym):
					grammemes = [word_info.tag.POS, word_info.tag.aspect, word_info.tag.case, word_info.tag.mood, word_info.tag.number, word_info.tag.person, word_info.tag.tense, word_info.tag.voice]
					tag = set(gram for gram in grammemes if gram is not None)
					syn_info = morph.parse(best_synonym)[0].inflect(tag)
					if syn_info is not None:
						text_out += syn_info.word
						text_out += ' '
						continue
		text_out += item
		text_out += ' '
	return text_out

def main():
	morph = pymorphy2.MorphAnalyzer()
	syn = Synonymizer()
	text_in = u'''Эксперты провели исследование трех российских социальных сетей: "ВКонтакте", "Одноклассники" и "Мой Мир". В ходе недельного исследования эксперты выяснили, что ребенку в возрасте 13 лет в соцсети "ВКонтакте" по запросу "порно" выдается список из закрытых групп, но при введении в поисковый запрос синонимов этого слова ребенок получает перечень открытых групп, содержащих информацию по запрашиваемой тематике, и может без проблем ее просмотреть. Кроме того, ребенок не застрахован от общения с педофилами в соцсети, может подвергаться моральному насилию и запугиванию, а также столкнуться с мошенниками. В социальной сети "Одноклассники" по запросу "порно" и его синонимов ребенку становится доступен список закрытых групп, в которые нельзя получить доступ. В этой социальной сети подросток может рассчитывать только на "легкую эротику". Общение с педофилами в "Одноклассниках" сведено к минимуму, а каких-либо видов мошенничества эксперты в сети не обнаружили'''
	text_out = make_text_clear(text_in, syn, morph)
	print("Input: %s" % text_in)
	print("Output: %s" % text_out)	

if __name__ == '__main__':
	main()
