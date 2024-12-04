"""
Create an FTL knowledge base.

Classes:
    KnowledgeBase - Stores a collection of same signature FTL formulas as ParseTrees.
"""
from ftlogic.core.signature import Signature
from ftlogic.core import parser

class KnowledgeBase:
    """
    Stores a collection of same signature FTL formulas as ParseTrees.
    
    Attributes
    ----------
    signature : Signature
        The signature over which the formulas are defined.
    formulas : list, optional
        A list of FTL formulas over the signature. Can be string or ParseTree representations (default is None).

    Methods
    -------
    add(formula)
        Attempts to add formula to the knowledge base.
    """
    def __init__(self, signature, formulas=None):
        """
        Constructs a KnowledgeBase object intialised from parameters.

        Parameters
        ----------
        signature : Signature
            The signature over which member formulas are written.
        formulas : list, optional
            A list of FTL formulas over the signature. Can be string or ParseTree representations (default is None).
        """
        self.signature = signature
        self.parseTrees = []

        for f in formulas:
            self.add(f)

    def __iter__(self):
        """
        Returns an iterable containing all parse trees in the knowledge base.

        Returns
        -------
        : iter
            An iterable containing all parse trees in the knowledge base.
        """
        return iter(self.parseTrees)
            
    def __len__(self):
        """
        Returns the number of formulas in the knowledge base.

        Returns
        -------
        : int
            The number of formulas in the knowledge base.
        """
        return len(self.parseTrees)
    
    def __contains__(self, formula):
        """
        Returns True if formula is in the knowledge base. False otherwise.

        Parameters
        ----------
        formula : str, ParseTree
            An FTL formula in string or parse tree form.

        Returns
        -------
        : bool
            True if formula is in the knowledge base. False otherwise.
        """
        try:
            if not isinstance(formula, parser.ParseTree):
                formula = parser.parse(formula, self.signature, onlyFormulas=True)
        except:
            return False
        
        return formula in self.parseTrees
    
    def add(self, formula):
        """
        Adds formula to the knowledge base.

        Parameters
        ----------
        formula : str, ParseTree
            An FTL formula in string or parse tree form.
        """
        if isinstance(formula, parser.ParseTree):
            if formula.signature != self.signature:
                raise ValueError("Formula signature must match knowledge base signature.")
            self.parseTrees.append(formula)
        else:
            try:
                pt = parser.parse(formula, self.signature, onlyFormulas=True)
                self.parseTrees.append(pt)
            except parser.ParseError as err:
                raise Exception(f"Could not parse formula {formula}. {err}")