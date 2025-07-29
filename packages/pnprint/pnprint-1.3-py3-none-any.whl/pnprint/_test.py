from . import *

def test_nformat():
	opts = dict(width=100)
	assert nformat([[1000,2324,30],[40000,5000,6342342]], **opts) == '[[1000, 2324, 30], [40000, 5000, 6342342]]'
	assert nformat(repr({
		'name': 'mydict',
		'comment': 'this is a dictionnary',
		'field': (5, 6),
		'long one': [12324232, 53445645645, 'truc', 345345345345345356, (456,45), 'bla bla bla', 'blo blo blo', 'things and so'],
		'some text': '/!\\  even content of strings is formated:\n  {345, 23, 17, [2,1]}  as you see\n',
		}), **opts) == "{\n\t'name': 'mydict',\n\t'comment': 'this is a dictionnary',\n\t'field': (5, 6),\n\t'long one': [\n\t\t12324232,\n\t\t53445645645,\n\t\t'truc',\n\t\t345345345345345356,\n\t\t(456, 45),\n\t\t'bla bla bla',\n\t\t'blo blo blo',\n\t\t'things and so'],\n\t'some text': '/!\\\\  even content of strings is formated:\\n  {345, 23, 17, [2,1]}  as you see\\n'}"

def test_deformat():
	input = '''
	P2 = vec3(0.08182,1.184e-08,-0.09931)
	P3 = vec3(-0.0431,1.258e-08,-0.1056)
P4 = vec3(-0.1593,-1.199e-08,0.1006)
line = [
	Segment(P4, P0),
	Segment(P0, P1 ),
	ArcThrough(P1, vec3(0.09681,-1.713e-09,0.01437), P2
		),
	Segment(P2,P3),
	ArcThrough(P3,vec3(-0.06933,-1.117e-09,0.009369),P4),
	]
axis = Axis(
	vec3(-0.1952,	4.918e-08,	-0.4126),
	vec3(1,	0,	0))
	'''
	output = 'P2 = vec3(0.08182,1.184e-08,-0.09931)\nP3 = vec3(-0.0431,1.258e-08,-0.1056)\nP4 = vec3(-0.1593,-1.199e-08,0.1006)\nline = [Segment(P4, P0), Segment(P0, P1), ArcThrough(P1, vec3(0.09681,-1.713e-09,0.01437), P2), Segment(P2,P3), ArcThrough(P3,vec3(-0.06933,-1.117e-09,0.009369),P4), ]\naxis = Axis(vec3(-0.1952, 4.918e-08, -0.4126), vec3(1, 0, 0))\n'
	assert deformat(input) == output
	
def test_ncolor():
	# for object dumping with string representation
	nprint(repr(dir()))
	
	# for common print use
	nprint('here is a list:', [[1000,2324,30],[40000,5000,6342342]], '\nhere is a type:', int, '\nhere is a Name in CamelCase and one in AVeryLongStringAndSoWhat')
	
	# for string and data output
	nprint('hello everyone, 100 is a decimal number and (0x27a) is an hexadecimal one between parentheses. (did you noticed the automatic line shift ?)')
	
	# complex structures
	data = {
		'name': 'mydict',
		'comment': 'this is a dictionnary',
		'field': (5, 6),
		'long one': [12324232, 53445645645, 'truc', 345345345345345356, (456,45), 'bla bla bla', 'blo blo blo', 'things and so'],
		'some text': '/!\\  even content of strings is formated:\n  {345, 23, 17, [2,1]}  as you see\n',
		}

	nprint('data structure: ', data)
	nprint('data structure: ', data, colors=red_orange)
	nprint('data structure: ', data, colors=False)

def test_ccolor():
	from textwrap import dedent
	cprint(dedent("""\
		_keywords = {'pass', 'and', 'or', 'if', 'elif', 'else', 'match', 'case', 'for', 'while', 'break', 'continue', 'is', 'in', 'not', 'def', 'lambda', 'class', 'yield', 'async', 'await', 'with', 'try', 'except', 'finally', 'raise', 'from', 'import', 'as', 'with', 'return', 'assert'}
		_constants = {'None', 'True', 'False', 'Ellipsis'}
		_private_start = '_'

		def ccolor(code:str, colors=None) -> str:
			''' colorize the given code by adding unix terminal codes for character coloration '''
			if colors is None:
				colors = globals()['colors']
			
			position = 0
			result = io.StringIO()
			while position < len(code):
				# use regex for looking forward and to jump fast in text
				if match := _call_pattern.match(code, position):
					result.write(colors.marker)
					result.write(code[match.start():match.end()-1])
					result.write(colors.normal)
					position = match.end()-1
				elif match := _number_pattern.match(code, position):
					result.write(colors.number)
					result.write(match.group())
					result.write(colors.normal)
					position = match.end()
				elif match := _string_pattern.match(code, position):
					result.write(colors.number)
					result.write(match.group())
					result.write(colors.normal)
					position = match.end()
				elif match := _comment_pattern.match(code, position):
					result.write(colors.comment)
					result.write(match.group())
					result.write(colors.normal)
					position = match.end()
				elif match := _word_pattern.match(code, position):
					word = match.group()
					# special names
					if word in _keywords:
						result.write(colors.keyword)
						result.write(word)
						result.write(colors.normal)
					elif word in _constants:
						result.write(colors.number)
						result.write(word)
						result.write(colors.normal)
					elif word.startswith(_private_start):
						result.write(colors.private)
						result.write(word)
						result.write(colors.normal)
					# normal names
					else:
						result.write(word)
					position = match.end()
				else:
					result.write(code[position])
					position += 1
			return result.getvalue()
			"""))
	text = dedent("""\
		def _bisect(l, index, key=lambda x:x):
			''' simple bisection over an array '''
			start,end = 0, len(l)
			while start < end:
				mid = (start+end)//2
				val = key(l[mid])
				if val < index:		start =	mid+1
				elif val > index:	end =	mid
				else:	return mid
			return start
		""")
	cprint(text, colors=blue_green)
	cprint(text, colors=red_orange)
