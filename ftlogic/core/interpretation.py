"""
Create FTL Interpetations and evaluate formulas.

Classes:
    Interpretation - Stores a structure, variable assignments, and domain assignments.

Methods:
    evaluate(parseTree, interpretation, junctors) - Returns truth value of formula.
    evaluateKB(knowledgeBase, interpretation, junctors, aggregator) - Returns truth value of knowledge base.
"""
from ftlogic.core import parser
from ftlogic.core.parser import NodeType
from ftlogic.core.knowledgebase import KnowledgeBase
from ftlogic import fuzzyops
import numpy as np
import tensorflow as tf
import copy 


class Interpretation:
    """
    Stores a complete set of constant, predicate, functor, variable, and domain mappings.
    
    Attributes
    ----------
    structure : Structure
        A Structure mapping constants, predicates, and functors.
    variableAssignment : dict
        Maps variable symbols to tensors.
    domainAssignment : dict
        Maps domain symbols to batches of tensors.

    Methods
    -------
    interpret(symbol):
        Returns the mapping of symbol.
    extend(substitution):
        Returns a copy of this Interpretation with variableAssignment updated to contain substitution.
    """
    def __init__(self, structure, variableAssignment=None, domainAssignment=None):
        """
        Constructs an Interpretation object intialised from parameters.

        Parameters
        ----------
        structure : Structure
            The Structure containing constant, predicate, and functor mappings.
        variableAssignment : dict, optional
            An initial set of mappings for variable symbols (default is None).
        domainAssignment : dict, optional
            An initial set of mappings for domain symbols (default is None).
        """
        self.structure = structure
        if variableAssignment:
            self.variableAssignment = variableAssignment
        else:
            self.variableAssignment = {}

        if domainAssignment:
            self.domainAssignment = domainAssignment
        else:
            self.domainAssignment = {}

    def __call__(self, symbol):
        """
        Returns the mapping of symbol.

        Parameters
        ----------
        symbol : str
            The symbol to map.

        Returns
        -------
        : any
            The mapping of symbol.
        """
        return self.interpret(symbol)
            
    def interpret(self, symbol):
        """
        Returns the mapping of symbol.

        Parameters
        ----------
        symbol : str
            The symbol to map.

        Returns
        -------
        : any
            The mapping of symbol.
        """
        if symbol in self.structure:
            return self.structure(symbol)
        elif symbol in self.variableAssignment:
            return self.variableAssignment[symbol]
        elif symbol in self.domainAssignment:
            return self.domainAssignment[symbol]
        else:
            raise ValueError(f"Symbol {symbol} is not interpretable.")
    
    def extend(self, substitution):
        """
        Returns a copy of this Interpretation with variableAssignment updated to contain substitution.

        Parameters
        ----------
        substitution : dict
            variable substitutions.

        Returns
        -------
        : Interpretation
            A copy of this Interpretation with variableAssignment updated to contain substitution.
        """
        variableAssignment = copy.copy(self.variableAssignment)
        variableAssignment.update(substitution)
        extInterpretation = Interpretation(self.structure,
                                           variableAssignment,
                                           self.domainAssignment)
        return extInterpretation


class EvaluationError(Exception):
    pass

def evaluateKB(knowledgeBase, interpretation, junctors, aggregator=fuzzyops.standardProductSet.universal):
    """
    Returns the satisfaction of knowledgeBase under interpretation using the junctors and aggregator.

    Parameters
    ----------
    knowledgeBase : KnowledgeBase
        The knowledge base to evaluate.
    interpretation : Interpretation
        An interpretation under which to evaluate knowledgeBase. Must map all symbols which appear in knowledgeBase formualas.
    junctors : OperatorSet
        A complete collection of differentiable fuzzy operators.
    aggregator: callable
        A differentiable function for aggregating batches of fuzzy truth values. (default is Standard Operator Set's universal quantification). 

    Returns
    -------
    : Tensor
    A tensorflow Tensor containing the fuzzy truth value of knowledgeBase evaluated under interpretation.
    """
    if not isinstance(knowledgeBase, KnowledgeBase):
        raise Exception("knowledgeBase must be of type KnowledgeBase.")
    
    results = []
    for pt in knowledgeBase.parseTrees:
        results.append(evaluate(pt, interpretation, junctors))

    return aggregator(tf.concat(results, 0))


def evaluate(parseTree, interpretation, junctors): 
    """
    Returns the truthfulness of parseTree under interpretation using the junctors.

    Parameters
    ----------
    parseTree : ParseTree
        The formula to evaluate as a ParseTree.
    interpretation : Interpretation
        An interpretation under which to evaluate the parse tree. Must map all symbols which appear in formula.
    junctors : OperatorSet
        A complete collection of differentiable fuzzy operators.

    Returns
    : Tensor
    A tensorflow Tensor containing the fuzzy truth value of parseTree under interpretation.
    """
    #Recursively evaluate the parse tree.
    if parseTree.type ==  NodeType.CONSTANT:
        return interpretation(parseTree.value)
    
    elif parseTree.type == NodeType.VARIABLE:
        return interpretation(parseTree.value)
    
    elif parseTree.type == NodeType.FUNCTOR or parseTree.type == NodeType.PREDICATE:
        childValues = []
        for child in parseTree.children:
            childValues.append(evaluate(child, interpretation, junctors))
        
        return interpretation(parseTree.value)(*childValues)
    
    #Evaluating compound formulas
    elif parseTree.type == NodeType.BRACKET:
        return evaluate(parseTree.children[0], interpretation, junctors)   
    
    elif parseTree.type ==  NodeType.NEGATION:
        operator = junctors.negation
        return operator(evaluate(parseTree.children[0], interpretation, junctors))
    
    elif parseTree.type ==  NodeType.CONJUNCTION:
        operator = junctors.tnorm
        return operator(evaluate(parseTree.children[0], interpretation, junctors),
                        evaluate(parseTree.children[1], interpretation, junctors))
    
    elif parseTree.type ==  NodeType.DISJUNCTION:
        operator = junctors.tconorm
        return operator(evaluate(parseTree.children[0], interpretation, junctors),
                        evaluate(parseTree.children[1], interpretation, junctors))
    
    elif parseTree.type ==  NodeType.IMPLICATION:
        operator = junctors.implication
        return operator(evaluate(parseTree.children[0], interpretation, junctors),
                        evaluate(parseTree.children[1], interpretation, junctors))
    
    #Evaluate quantifiers
    elif parseTree.type ==  NodeType.EXISTENTIAL or parseTree.type == NodeType.UNIVERSAL:
        boundVariable = parseTree.value[0]
        domainSymbol = parseTree.value[1]
        
        results = []
        #Iterate over the various values the now bound value can take and evaluate the subformula.
        domain = interpretation(domainSymbol)
        for i in range(0, domain.shape[0]):
            variableValue = domain[i:i+1]
            substitution = {}
            substitution[boundVariable] = variableValue
            extInterpretation = interpretation.extend(substitution)
            results.append(evaluate(parseTree.children[0], extInterpretation, junctors))

        aggregator = None
        if parseTree.type == NodeType.EXISTENTIAL:
            aggregator = junctors.existential
        elif parseTree.type == NodeType.UNIVERSAL:
            aggregator = junctors.universal

        return aggregator(tf.concat(results, 0))
        
    else:
        raise EvaluationError(f"Unsupported node type '{parseTree.type}'.")
