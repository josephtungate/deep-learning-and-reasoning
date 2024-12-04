"""
Create FTL structures.

Classes:
    Structure - Stores predicate, functor, and constant mappings for elements of a Signature.
"""
from ftlogic.core.signature import Signature

class Structure:
    """
    Stores predicate, functor, and constant mappings for elements of a Signature.
    
    Attributes
    ----------
    signature : Signature
        The Signature whose elements are mapped by this structure.
    mappings : dict
        Maps constants to tensors, functors to tensor-valued functions, and predicates to fuzzy truth-valued functions.
    complete : bool
        True only if every element in signature is mapped by mappings.
    """

    def __init__(self, signature, mappings=None):
        """
        Constructs a Structure object intialised from parameters.

        Parameters
        ----------
        signature : Signature
            The Signature whose elements are mapped by this structure.
        mappings : dict, optional
            An initial set of mappings for symbols in signature (default is None).
        """
        self.signature = signature
        self.mappings = {}
        if mappings:
            self.mappings = mappings

    @property
    def complete(self):
        for p in self.signature.predicates.keys():
            if not p in self.mappings:
                return False
            
        for f in self.signature.functors.keys():
            if not f in self.mappings:
                return False
        
        for c in self.signature.constants:
            if not c in self.mappings:
                return False
            
        return True
    
    def __contains__(self, symbol):
        """
        True if symbol is mapped by this Structure. Otherwise False.

        Parameters
        ----------
        symbol : str
            The symbol to check for inclusion.

        Returns
        -------
        : bool
            True if symbol is mapped by this Structure. Otherwise False.
        """
        return symbol in self.mappings
    
    def __call__(self, symbol):
        """
        Returns the mapping of symbol in mappings.

        Parameters
        ----------
        symbol : str
            The symbol to map.

        Returns
        -------
        : any
            The mapping of symbol in mappings.
        """
        return self.mappings[symbol]
    
    def __eq__(self, other):
        """
        True if other is a Structure with equivalent signature and mappings. Otherwise False.

        Parameters
        ----------
        other : Structure
            The Structure to compare.

        Returns
        -------
        : bool
            True if other is a Structure with equivalent signature and mappings. Otherwise False.
        """
        if isinstance(other, Structure):
            return (self.signature == other.signature
                    and self.mappings == other.mappings)
        return False
    




