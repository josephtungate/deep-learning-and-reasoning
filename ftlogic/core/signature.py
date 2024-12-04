"""
Create FTL signatures.

Classes:
    Signature - Stores predicate, functor, and constant symbols alongside their arities.
"""
class Signature:
    """
    Stores predicate, functor, and constant symbols alongside their arities.
    
    Attributes
    ----------
    predicates : dict
        Contains predicate symbol (str) to arity (int) mappings.
    functors : dict
        Contains functor symbol (str) to arity (int) mappings.
    constants : list
        A list of constant symbols (str).    
    """

    def __init__(self, predicates=None, functors=None, constants=None):
        """
        Constructs a Signature object intialised from parameters.

        Parameters
        ----------
        predicates : dict, optional
            Contains predicate symbol (str) to arity (int) mappings (default is None).
        functors : dict, optional
            Contains functor symbol (str) to arity (int) mappings (default is None).
        constants : list, optional
            A list of constant symbols (str) (default is None).   
        """
        self.predicates = {}
        self.functors = {}
        self.constants = {}

        if predicates:
            self.predicates = predicates
        if functors:
            self.functors = functors
        if constants:
            self.constants = constants


    def __contains__(self, symbol):
        """
        True if symbol is in this Signature. Otherwise False.

        Parameters
        ----------
        symbol : str
            The symbol to check for inclusion.

        Returns
        -------
        : bool
            True if symbol is in this Signature. Otherwise False.
        """
        return (symbol in self.predicates 
            or symbol in self.functors or
            symbol in self.constants)
    
    def __eq__(self, other):
        """
        True if other is a Signature containing the same symbols and arities. Otherwise False.

        Parameters
        ----------
        other : Signature
            The Signature to compare.

        Returns
        -------
        : bool
            True if other is a Signature containing the same symbols and arities. Otherwise False.
        """
        if isinstance(other, Signature):
            return (self.predicates == other.predicates
                    and self.functors == other.functors
                    and self.constants == other.constants)
        
        return False