
def create_network():
	"""
	"""

	x = {'AA': {'AB': 0,
	            'BA': 0},
	     'BA': {'AB': 0,
	            'BB': 0,
	            'CA': 0},
	     'AB': {'AA': 0,
	            'BA': 0,
	            'BB': 0,
	            'BC': 0,
	            'AC': 0}
	    }

	return x