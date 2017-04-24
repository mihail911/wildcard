import csv
from itertools import product
from collections import Counter
import matplotlib.pyplot as plt

plt.rcParams['patch.edgecolor'] = "black"
filename = "../data/command_distribution_breakdown.tsv"
lines = [ line for line in csv.reader( open(filename,'r') , delimiter="\t" ) ]

total = len(lines) - 1
count_pickup = len([ line for line in lines if "pickup" in line[-1] ]) 
count_drop = len([ line for line in lines if "drop" in line[-1] or "keep" in line[-1] ])
count_search = len([ line for line in lines if "search" in line[-1] ])
count_convo = len([ line for line in lines if "convo" in line[-1] ]) 
count_meet = len([ line for line in lines if "meet" in line[-1] ])

all_goals = set([line[-1] for line in lines])
all_command_types = set([line[-2].strip() for line in lines])


#print("all goals",all_goals)
#print("all command types",all_command_types)

'''
print("total",total)
print("pickup",count_pickup)
print("drop",count_drop)
print("search",count_search)
print("convo",count_convo)
'''

actions_map = { "drop":"drop" , "keep":"drop"
 , "convo":"convo", "pickup":"pickup" , "rules":"misc" , "meet":"misc" , "move":"misc" , "search":"search" , "misc":"misc" }
command_type_to_viz_hatch = { "imperative":"/" , "locative":"" , "performative":"x" }  
command_type_to_viz_color = { "imperative":'yellowgreen', "performative":'lightskyblue', "locative":'lightcoral'}
all_command_types = [ "locative" , "imperative" , "performative" ]
command_types_to_colors = { key:"white" for key in all_command_types }

def map_actions(action):
	return actions_map.get(action)

def get_action_to_command_type_pairing(line):

	actions = [ elem.strip() for elem in line[-1].split(";") ] 
	command_types = [ elem.strip() for elem in line[-2].split(",") ]

	pairings = None
	if len(actions) == 2 and len(command_types) == 2:
		pairings = [ tup for tup in zip(actions,command_types) ]
	else:
		pairings = [ tup for tup in product(actions,command_types) ]

	return pairings

def count_action_to_command_type(lines):

	all_pairings = [ (map_actions(a),ct) for line in lines for a,ct in get_action_to_command_type_pairing(line) ]

	action_to_command_type = {}
	for a,ct in all_pairings:
		if a in action_to_command_type:
			action_to_command_type[a].append(ct)
		else:
			action_to_command_type[a] = [ct]

	for key in action_to_command_type:
		action_to_command_type[key] = Counter(action_to_command_type[key])

	return action_to_command_type

counters = count_action_to_command_type(lines[1:])


def generate_pie_chart_for_counter(counter,savename="default_save.png"):

	command_types,sizes = zip(*[ (key,counter[ key ]) for key in all_command_types if counter[key] != 0 ])

	patches, texts, autotexts = plt.pie(sizes, startangle=90 , autopct='%1.1f%%' , textprops={ "weight":"bold" , "fontsize":20 } )

	for i in range(0,len(patches)):
		ct = command_types[i]
		patches[i].set_color(command_type_to_viz_color[ct])
		patches[i].set_hatch(command_type_to_viz_hatch[ct])
	
	plt.legend(patches, command_types, loc="lower right", bbox_to_anchor = (1.0, -.1), fontsize=22)
	plt.axis('equal')
	plt.savefig(savename)
	plt.clf()
	#plt.show() 

for key in counters:
	savename="%s_command_distribution" %key
	generate_pie_chart_for_counter(counters[key],savename=savename)




