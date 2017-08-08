import itertools
import os


class Color:
   """
   Basic utility for colored printing
   """
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   END = '\033[0m'

   color_map = {"green": GREEN,
                "yellow": YELLOW,
                "red": RED,
                }

   def color_str(self, str, color="green"):
      return Color.color_map[color] + str + Color.END
