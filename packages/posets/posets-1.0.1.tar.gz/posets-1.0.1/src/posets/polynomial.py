'''@no_doc@no_children@'''
import math
import itertools

class Polynomial:
	r'''
	A class encoding polynomials in noncommutative variables (used by the \verb|Poset| class to compute the \cv\dv-index).

	This class is basically a wrapper around a dictionary representation for polynomials (e.g. $3\av\bv+2\bv\bv$ is encoded as \verb|{'ab':3, 'bb':2}|).
	The class provides methods for basic arithmetic with polynomials, to substitute a polynomial
	for a variable in another polynomial and to convert \av\bv-polynomials to \cv\dv-polynomials (when possible) and vice versa. You can also get and set
	coefficients as if a polynomial were a dictionary.
	@is_section@
	'''
	def __init__(this, data=None):
		r'''
		Returns a \verb|Polynomial| given either a dictionary or a list of pairs.

		If \verb|data| is a dictionary then the keys are the monomials and the values are the coefficients.
		If \verb|data| is a list then all elements should be of the form \verb|[c,m]| where \verb|c| is a coefficient and \verb|m| is a string representing a monomial.
		If \verb|data| is \verb|None| then the zero polynomial is returned.
		'''
		this.data = {} if data==None else data if type(data)==dict else {d[1]:d[0] for d in data}

	def _to_poly(*args):
		r'''
		Iterator that converts elements of a list to instances of \verb|Polynomial|.

		Internal method used by \verb|__mul__| and \verb|__add__|.
		'''
		for x in args:
			if isinstance(x,Polynomial): yield x
			elif type(x) in (int,float): yield Polynomial({'':x})
			elif hasattr(x,'__iter__'): yield Polynomial(x)
			else: yield Polynomial({})

	def strip(this):
		'''
		Removes any zero terms from a polynomial in place and returns it.
		'''
		for m,c in list(this.data.items()):
			if c==0: del this.data[m]
		return this

	def __mul__(*args):
		'''
		Noncommutative polynomial multiplication.
		'''
		return Polynomial.__add__(
			*(
			Polynomial(
				{''.join(map(lambda y:y[0],x)) :
				math.prod(map(lambda y:y[1],x))}
				)
			for x in itertools.product(*map(lambda y:y.data.items(),Polynomial._to_poly(*args)))
			)
			).strip()
	__rmul__=__mul__

	def __pow__(this,x):
		r'''
		Polynomial exponentiation by non-negative integers.

		Raises \verb|NotImplementedError| if either \verb|x| is
		not an integer or \verb|x<0|.
		'''
		if type(x)!=int or x<0: raise NotImplementedError
		return Polynomial.__mul__(*itertools.repeat(this,x)).strip()

	def __add__(*args):
		'''
		Polynomial addition.
		'''
		ret = {}
		for p in Polynomial._to_poly(*args):
			for m,c in p.data.items():
				if m in ret: ret[m]+=c
				else: ret[m]=c
		return Polynomial(ret).strip()
	__radd__=__add__

	def __neg__(this):
		return Polynomial({m:-c for m,c in this.data.items()})

	def __sub__(this, that):
		'''Polynomial subtraction'''
		return (this+(-that)).strip()

	def __ge__(this, that):
		r'''
		Returns \verb|True| if \verb|this| is coefficientwise
		greater than or equal
		to \verb|that|.
		'''
		if isinstance(that, int):
			return all(v >= that for v in this.data.values())
		if isinstance(that, Polynomial):
			return all((m in this and this[m]>=that[m]) or (that[m]<=0) for m in that)

	def __gt__(this, that):
		r'''
		Returns \verb|True| if \verb|this| is greater than or equal
		to \verb|that| coefficientwise and \verb|this| is not equal
		to \verb|that|.
		'''
		if isinstance(that, int):
			return all(v > that for v in this.data.values())
		if isinstance(that, Polynomial):
			return this!=that and all((m in this and this[m]>=that[m]) or (that[m]<=0) for m in that)

	def __le__(this, that):
		r'''
		Returns \verb|True| if \verb|this| is coefficientwise less or
		equal to \verb|that|.
		'''
		if isinstance(that, int):
			return all(v <= that for v in this.data.values())
		if isinstance(that, Polynomial):
			return all((m in this and this[m]<=that[m]) or (that[m]>=0) for m in that)

	def __lt__(this, that):
		r'''
		Returns \verb|True| if \verb|this| is coefficientwise less or
		equal to \verb|that| and \verb|this| and \verb|that| or not equal.
		'''
		if isinstance(that, int):
			return all(v < that for v in this.data.values())
		if isinstance(that, Polynomial):
			return this!=that and all((m in this and this[m]<=that[m]) or (that[m]>=0) for m in that)


	def sub(this, poly, monom):
		r'''
		Returns the polynomial obtained by substituting the polynomial \verb|poly| for the monomial \verb|m| (given as a string) in \verb|this|.
		'''
		ret = Polynomial({}) #initialize to zero
		for m,c in this.data.items():
			r = [['',c]] #term to add to ret, starts as coefficient
			monom_iter = iter(monom)
			curr_char = next(monom_iter)
			last_char_ind = 0 #start of char block being read
			curr_ind = 0 #current index
			for v in m: #loop through chars looking for monom
				curr_ind += 1
				if v==curr_char:
					try:
						curr_char = next(monom_iter)
					except StopIteration:
						r = Polynomial._prepoly_mul_poly(r,poly)
						monom_iter = iter(monom)
						curr_char = next(monom_iter)
						last_char_ind = curr_ind
				else:
					s = m[last_char_ind:curr_ind]
					for x in r: x[0]+=s #multiply r by the variables in the buffer
					last_char_ind = curr_ind
			#if m ended in a partial match need to dump buffer
			if last_char_ind != curr_ind:
				s = m[last_char_ind:]
				for x in r: x[0]+=s
			Polynomial._poly_add_prepoly(ret,r) #add the poly to ret
		ret.data = {k:v for k,v in ret.data.items() if v!=0}
		return ret.strip()

	def _poly_add_prepoly(p, q):
		r'''Internal backend for \verb|__add__|.'''
		for m,c in q:
			p[m] = c + (p[m] if m in p else 0)
	def _prepoly_mul_poly(q, p):
		r'''Internal backend for \verb|__mul__|.'''
		return [[x[0][0]+x[1][0], x[0][1]*x[1][1]] for x in itertools.product(q,p.data.items())]

	def abToCd(this):
		r'''
		Given an \av\bv-polynomial returns the corresponding \cv\dv-polynomial if possible and the given polynomial if not.
		'''
		if len(this.data)==0: return this
		#substitue a->c+e and b->c-e
		#where e=a-b
		#this scales by a factor of 2^deg
		ce = this.sub(Polynomial({'c':1,'e':1}),'a').sub(Polynomial({'c':1,'e':-1}),'b')

		cd = ce.sub(Polynomial({'cc':1,'d':-2}),'ee')
		#check if any e's are still present
		for m in cd.data:
			if 'e' in m:
				return this
		#divide coefficients by 2^n
		for monom in cd.data.keys(): break #grab a monomial
		power=sum(2 if v=='d' else 1 for v in monom)
		return Polynomial({k:v>>power for k,v in cd.data.items()})

	def cdToAb(this):
		r'''
		Given a \cv\dv-polynomial returns the corresponding \av\bv-polynomial.
		'''
		return this.sub(Polynomial({'a':1,'b':1}), 'c').sub(Polynomial({'ab':1,'ba':1}),'d')

	def __len__(this):
		'''Returns the number of coefficients.'''
		return len(this.data)

	def __iter__(this):
		return iter(this.data)

	def __getitem__(this,i):
		return this.data[i]

	def __setitem__(this,i,value):
		this.data[i] = value

	def __bool__(this):
		for k in this.data:
			if k!='' or this.data[k]: return True
		return False

	def __str__(this):
		this.strip()
		data = list(this.data.items())
		if len(data)==0: return '0'
		data.sort(key=lambda x:x[0])
		m,c = data[0]
		ret=[Polynomial._coeff_str(c), Polynomial._monom_str(m)]
		for m,c in data[1:]:
			try:
				if c>0: ret.append('+')
			except:
				ret.append('+')
			ret.append(Polynomial._coeff_str(c))
			ret.append(Polynomial._monom_str(m))
		return ''.join(ret)
			
	def _monom_str(m):
		current = ''
		power = 0
		ret = []
		for c in m:
			if current == '':
				current = c
				power = 1
				continue
			if c == current:
				power += 1
				continue
			ret.append(current)
			if power != 1:
				ret.append('^{')
				ret.append(str(power))
				ret.append('}')
			current = c
			power = 1
		ret.append(current)
		if power != 1 and power != 0:
			ret.append('^{')
			ret.append(str(power))
			ret.append('}')
		if power == 0 and current == "":
			ret.append('1')
		return ''.join(ret)

	def _coeff_str(c):
		ret = []
		try:
			if c<0:
				c=-c
				ret.append('-')
		except:
			pass
		if c==1: return ''
		sc=str(c)
		if any(x in sc for x in ('+','-',' ')):
			ret.append('(')
			ret.append(sc)
			ret.append(')')
		else:
			ret.append(sc)
		return ''.join(ret)

#	def __str__(this):
#		this.strip()
#		data = list(this.data.items())
#		data.sort(key=lambda x:x[0])
#		s = ""
#		for i in range(0,len(data)):
#			if not data[i][1]==0: continue
#			if data[i][1] == -1 or data[i][1] == Polynomial({'':-1}): s+= '-'
#			if isinstance(data[i][1],Polynomial) and data[i][1]!=Polynomial({'':1}): s+='('+str(data[i][1])+')'
#			elif data[i][1]-1: s += str(data[i][1])
#			current = ''
#			power = 0
#			for c in data[i][0]:
#				if current == '':
#					current = c
#					power = 1
#					continue
#				if c == current:
#					power += 1
#					continue
#				s += current
#				if power != 1: s += '^{' + str(power) + '}'
#				current = c
#				power = 1
#			s += current
#			if power != 1 and power != 0: s += '^{' + str(power) + '}'
#			if power == 0 and current == "": s += '1'
#
#			if i != len(data)-1:
#				if data[i+1][1] >= 0: s += "+"
#		if s == '': return '0'
#		return s
#
	def __repr__(this):
		return 'Polynomial('+repr(this.data)+')'

	def __eq__(this,that):
		return (isinstance(that,type(this)) and this.strip().data == that.strip().data) or this.data == {'':that}
