"""
Basic utility for colored printing
"""

class Color:
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   END = '\033[0m'

def color_str(str, color=Color.GREEN):
   return color + str + Color.END