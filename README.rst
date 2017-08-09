=========
Wild Card
=========
  This is the accompanying code for the paper: 
  ::

  | Matthew Lamm* and Mihail Eric*. The Pragmatics of Indirect Commands in Collaborative Discourse. 
  | International Conference on Computational Semantics (IWCS) 2017 (to appear). 
  | https://arxiv.org/abs/1705.03454.
  
   
   
  In this paper we performed a systematic study of the various indirect command types present in the `Cards Corpus <http://cardscorpus.christopherpotts.net/>`_. We developed models demonstrating that well-formulated notions of common ground discourse can be useful for pragmatically disambiguating certain dialogue exchanges. For more details, please read our paper!
 
  
Structure
---------
  The code in the repository contains the following package structure:

  - *test* (unit/integration tests)
  - *wildcard* (root directory)
     - *scripts* (miscellaneous scripts)
     - *model* (any relevant model files)
     - *util* (various utility modules)
  
Setup
--------

Conda
^^^^^
::

   # Create a new environment
   conda create -name wildcard
   source activate wildcard
   # Install libraries needed to run code within environment
   pip install -r requirements.txt
   # Run setup.py and you should be good to go!
   python setup.py install
   
