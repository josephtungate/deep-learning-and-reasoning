Readme.txt
Thank you for downloading ftlogic.

INSTALLATION INSTRUCTIONS
In order to use ftlogic on your own machine, please do the following:
> Install Python3.
> Install TensorFlow2, numpy, matplotlib, jupyterlab, and their dependencies.
> Add ftlogic to your machine's PYTHON_PATH variable.

If done correctly, you should be able to import ftlogic and its subpackages.
Please note that TensorFlow2 can take a while to initialise which may cause ftlogic import statements to hang for a minute or two.

FTLOGIC CONTENTS
ftlogic contains two subpackages, core and fuzzyops. 
core contains the following modules:
    - interpretation.py - Contains an Interpretation class enabling users to create Fuzzy Tensor Logic interpretations. 
        Additionally contains methods for evaluating the truthfulness of formulas and knowledge bases.
    - knowledgebase.py - Contains a KnowledgeBase class enabling users to compile Fuzzy Tensor Logic formulas into knowledge bases for training and querying.
    - model.py - Contains a Model class enabling users to build, train, and query Fuzzy Tensor Logic agents.
    - parser.py - Contains a ParseTree class which is used to store parse trees of Fuzzy Tensor Logic expressions.
        Additionally contains a parse method for parsing formulas into ParseTree objects.
    - signature.py - Contains a Signature class, enabling users to create Fuzzy Tensor Logic signatures.
    - structure.py - Contains a Structure class, enabling users to create Fuzzy Tensor Logic structures over a signature.

fuzzyops contains a single module operators.py.
operators.py contains a wide variety of fully differentiable fuzzy logic operators including
negations, t-norms, t-conorms, fuzzy implications, and existential and universal aggregators.
These operators are implemented as Python functions which make use of Tensorflow 2 methods to ensure differentiability.
Additionally, the module contains an OperatorSet class which allows users to compile a selection of fuzzy operators for use in evaluating formulas.
For the user’s convenience, the module contains a OperatorSet object implementing the recommended Standard Product Set.

OTHER CONTENTS
This download also contains example systems in the example_systems subdirectory.

FURTHER READING
Please see Deep Learning and Reasoning for more details.