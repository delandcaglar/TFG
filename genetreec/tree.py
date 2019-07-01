import indicator
import random
import pandas as pd
import math
import tagger
import copy


deepness = 5
data = pd.read_csv('tagged_data/SAN.csv')
indivector = indicator.indivector()

def entropy(v):           # v is the class proportion (frec/total)
	if v==0 or v==1:      #    Just works with 2-classes problem
		return 0
	return -(v*math.log(v,2)+(1-v)*math.log(1-v,2))




class Genetreec:
	root = None #first Node
	data = None #reference to data
	index = 0 #tree index in the population

	def __init__(self, ind):
		self.root = Leaf([True] * data.shape[0])
		self.index = ind

	def train(self):
		self.root = self.root.train(deepness)
		self.root.setLeaveActions()
		#self.root.plot()

	def test(self, data):
		return None

	def evaluate(self):
		return self.root.evaluate()

class Node:
	func = None  #func to evaluate to split the data
	pivot = None    #value to split the data

	right = None   #node or leaf positive
	left = None    #node or leaf negative

	def __init__(self, func, pivot, right, left):
		self.func = func
		self.pivot = pivot
		self.right = right
		self.left = left

	def setLeaveActions(self):
		self.right.setLeaveActions()
		self.left.setLeaveActions()

	def evaluate(self):
		return None

	def plot(self):
		print('---- Function ' + self.func.name() + ' < ' + str(self.pivot) + ' ----')
		self.left.plot()
		print('\n')
		print('---- Function ' + self.func.name() + ' >= ' + str(self.pivot) + ' ----')
		self.right.plot()



class Leaf:
	tag = None 			#the final tag the data on the leaf will be classificated as (Used just when the tree is tagged)
	partition = None	#the boolean vector that represent data (data at branch) over df (data at root)
	action = None		#the action to do if an instance arrives

	def __init__(self, partition):
		self.partition = partition


	def train(self, levels): # Take the actual partition and a new function indicator, calculate the entropic pivot and split into 2 leaves
		func = copy.deepcopy(indivector[random.randint(0,9)])
		(criteria, pivot) = self.select_pivot(func.getValues())
		if isinstance(criteria, int): # Fail recieved, pivot to split not found, return the leaf (except first leave)
				if deepness == levels:    # If first leave, restart the search of func and pivot
					ret_node = self.train(levels)
				else:
					ret_node = self
		else:		# Pivot found, return the Node with two son leaves
			right = Leaf(criteria & self.partition)
			left = Leaf(~criteria & self.partition)

			if levels>1 :
				right = right.train(levels-1)
				left = left.train(levels-1)
			ret_node = Node(func, pivot, right, left)
		return ret_node

	def select_pivot(self, values):
		max_val = values['values'].min()
		min_val = values['values'].max()
		grill = [(max_val - min_val)*(x/10)+min_val for x in range(1,10)]   # Make a grill to test pivots
		grill_entropy = []

		total = sum(self.partition)

		total_inverse = 1 / total
		for x in grill:								# For each point on grill
			n_left  = sum(values['values'][self.partition] < x)		# Calculate left and right data
			n_right = sum(values['values'][self.partition] >= x)	# Calculate the first class frecuency on both

			# Calculate the total entropy and save to take the best
			if n_left < 3: # To few data to split, dont waste time calculating entropy
				l_entropy = 1
				r_entropy = 1
			else:
				if n_right < 3:  # To few data to split, dont waste time calculating entropy
					l_entropy = 1
					r_entropy = 1
				else:
					r_entropy = n_right* total_inverse * entropy( sum( (values['values'][self.partition]>=x) & (values['tag'][self.partition]<0)) / n_right )
					l_entropy  = n_left*total_inverse * entropy( sum( (values['values'][self.partition]<x)  & (values['tag'][self.partition]<0)) / n_left )

			grill_entropy.append(l_entropy + r_entropy)

		min_index = grill_entropy.index(min( grill_entropy ))
		pivot = grill[min_index]
		criteria = values['values'] < pivot			# Take the best pivot and make the boolean vector of the left leaf
		data_count = sum(criteria & self.partition)
		if data_count < 3 or sum(self.partition)-data_count < 3: # To few data to split
			return (0,0)

		return (criteria, pivot)					# Return the pivot and vector.

	def setLeaveActions(self):
		global data
		df = data[self.partition]
		sell_df = sum(df['tag'] > 0)
		buy_df = sum(df['tag'] < 0)
		double_sell_df = sum(df['tag'] > 1)
		double_buy_df = sum(df['tag'] < -1)
		action_sum = sell_df - buy_df + double_sell_df - double_buy_df / (sell_df + buy_df)

		if action_sum > 0:
			if action_sum <= 2:
				self.tag = 'Stop'
			else:
				self.tag = 'Sell'
		else:
			if action_sum >= -2:
				self.tag = 'Stop'
			else:
				self.tag = 'Buy'
		self.partition = None

	def evaluate(self):
		return self.tag

	def plot(self):   # Future graphical plot. By now, print the tag
		global data
		print(self.tag)
		return None
