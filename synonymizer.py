# -*- coding: utf-8 -*-

import codecs
import MySQLdb
import xml.etree.ElementTree as ET

class Synonymizer:
	def __init__(self):
		self.con = MySQLdb.connect(host="localhost", user="root", passwd="newpass", db="nlp", charset = "utf8")
		self.cur = self.con.cursor()
		self.cur.execute('SET NAMES utf8')
		self.lexmin_list = self.load_lexmin_list('data\lexmin.txt')
		self.similarity_dict = self.load_similarity_dict('data\similarity.txt')
		self.word_freq_list = self.load_word_freq_list('data\word_freq.txt')
		self.yarn_synonyms = self.load_yarn_synonyms('data\yarn.xml')
		print "Initialized"

	def __del__(self):
		self.con.close()
	
	def load_lexmin_list(self, name):
		lexmin_list = set()
		f = codecs.open(name, mode='r', encoding='utf-8')
		for line in f:
			word = line.strip() # remove \n at the end
			lexmin_list.add(word)
		f.close()
		return lexmin_list

	def is_lexmin(self, word):	
		return word in self.lexmin_list
			
	def load_similarity_dict(self, name):	
		similarity_dict = {}
		f = codecs.open(name, mode='r', encoding='utf-8')
		for line in f:
			lst = line.split(';') # [word1] [word2] [similarity rate]
			similarity_dict[(lst[0], lst[1])] = lst[2]
		return similarity_dict
			
	def get_similarity_rate(self,word1, word2):
		return self.similarity_dict.get((word1, word2))
			
	def load_word_freq_list(self, name):	
		word_freq_dict = {}
		f = codecs.open(name, mode='r', encoding='utf-8')
		for line in f:
			pair = line.split() # [word] [freq]
			word_freq_dict[pair[0]] = pair[1]
		return word_freq_dict
	
	def get_word_freq(self,word):
		return self.word_freq_list.get(word)	
	
	def load_yarn_synonyms(self, name):
		tree = ET.parse(name)
		root = tree.getroot()
		words_list = {}
		synsets_list = []
		words = root.find('words')
		for wordEntry in words.findall('wordEntry'):
			words_list[wordEntry.get('id')] = wordEntry.find('word').text
		synsets = root.find('synsets')
		for synsetEntry in synsets.findall('synsetEntry'):
			synset = set()
			for word in synsetEntry.findall('word'):
				synset.add(word.get('ref'))
			synsets_list.append(synset)
		
		yarn_synonyms = {}
		for id, word in words_list.items():
			for synset in synsets_list:
				if id in synset:
					yarn_synonyms[word] = set()
					for syn_id in synset:
						if id == syn_id:
							continue
						elif words_list.get(syn_id):
							yarn_synonyms[word].add(words_list[syn_id])
		return yarn_synonyms	
		
	def get_yarn_synonyms(self, word):	
		return self.yarn_synonyms.get(word)
		
	def get_synonyms(self, word):
		#synonyms from 'Synonymizer' DB
		synonyms = []
		self.cur.execute("""SELECT word_hash FROM clear_words WHERE word = %s""", (word, ))
		if self.cur.rowcount:   
			word_id = self.cur.fetchone()    
			self.cur.execute("""SELECT syn FROM clear_links WHERE word = %s ORDER BY weight DESC""", (word_id[0], ))
			if self.cur.rowcount:
				syns_id = self.cur.fetchall()
				for id in syns_id:
					self.cur.execute("""SELECT word FROM clear_words WHERE word_hash = %s""", (id[0], ))
					if self.cur.rowcount:
						syn = self.cur.fetchone()
						synonyms.append(syn[0])
		all_synonyms = set(synonyms)
		#synonyms from 'YARN'
		if self.get_yarn_synonyms(word):	
			all_synonyms.update(set(self.get_yarn_synonyms(word)))
		return list(all_synonyms)
	
	def filter_synonyms(self, word, syns):
		filtered_syns = []
		for syn in syns:
			if self.is_lexmin(syn) and self.get_similarity_rate(word, syn) and self.get_word_freq(syn): 
				filtered_syns.append(syn)
		return filtered_syns
		
	def sort_by_weight(elf, syn_weight_pair):
		return syn_weight_pair[1] # [synonym] [weight]
	
	def range_synonyms(self, word, syns):
		#synonyms are present in lexmin_list, both synonyms dictionaries 
		#(synonymizer and yarn), similarity_dict and word_freq_list
		ranged_syns = []
		for syn in syns:
			weight = int(self.get_word_freq(syn)) * float(self.get_similarity_rate(word, syn))
			ranged_syns.append((syn, weight))	
		ranged_syns.sort(key=self.sort_by_weight, reverse=True)	
		return ranged_syns
	
	def need_replace(self, word, best_syn):
		#assume: similarity_rate_word_with_itself = similarity_rate_word_with_the_best_synonym
		return not self.is_lexmin(word) or not self.get_word_freq(word) or self.get_word_freq(best_syn)>self.get_word_freq(word)
	
	def synonymize(self, word):	
		return self.range_synonyms(word, self.filter_synonyms(word, self.get_synonyms(word)))
