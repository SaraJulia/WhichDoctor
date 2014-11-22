from flask import Flask, render_template, redirect, request
from sqlalchemy import func, or_, create_engine, select, cast
import model
import re

# words that are common and don't mean anything important
toss_words = ['doctor', 'room', 'care']

ENGINE = create_engine("postgresql+pg8000://postgres:1234@localhost/medicare_claims", echo=False)

def split_terms(term):
	term_list = term.split()
	print term_list

	query_terms = ''

	for word in term_list:
		word = word.lower()

		#check if word is important or not
		if word not in toss_words:
			# add it to list of query terms
			query_terms = query_terms + word + " | "

	query_terms = query_terms[:-2]

	return query_terms


def specialty(term):
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)

	# search for specialties in the lookup table
	specialty_list = conn.execute(select([model.SpecialtyLookup.specialty])\
		.where(model.SpecialtyLookup.search_tsv.match(query_terms,postgresql_reconfig='english'))).fetchall()
	if specialty_list == []:
		return None
	else:
		return [specialty[0] for specialty in specialty_list]

def procedure(term):
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)

	code_list = conn.execute(select([model.Procedure.hcpcs_code])\
		.where(model.Procedure.hcpcs_tsv.match(query_terms,postgresql_reconfig='english'))).fetchall()
	if code_list == []:
		return None
	else:
		return [code[0] for code in code_list]
	

def main():
	pass
	#search_specialty('primary heart brain ear doctor')

if __name__ == '__main__':
	main()

"""
THIS IS HOW WE QUERY NOW:

>>> select_thing = select([SpecialtyLookup.specialty]).where(SpecialtyLookup.search_tsv.match('urology',postgresql_reconfig='english'))
>>> conn = ENGINE.connect()
>>> result = conn.execute(select_thing).fetchall()

result is a list of tuples
or = |
and = & 
the whole query:  
specialties = conn.execute(select([SpecialtyLookup.specialty]).where(SpecialtyLookup.search_tsv.match('eye | brain',postgresql_reconfig='english'))).fetchall()

"""