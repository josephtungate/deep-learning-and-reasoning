"""
Parse formulas into parse trees.

Classes:
    NodeType - An enum listing all possible parse tree node types.
    ParseTree - Stores parse tree representations of FTL expressions.

Methods:
    parse(formula, signature, precedence=_STANDARD_PRECEDENCE, junctorSymbols=_STANDARD_JUNCTOR_SYMBOLS, onlyFormulas=False) - Parses FTL expressions into parse trees.
"""
import re
from enum import Enum
from ftlogic.core.signature import Signature

class NodeType(Enum):
    """Enumerates all possible types of nodes which can appear in parse trees."""
    UNIVERSAL = 1,
    EXISTENTIAL = 2,
    IMPLICATION = 3,
    DISJUNCTION = 4,
    CONJUNCTION = 5,
    NEGATION = 6,
    PREDICATE = 7,
    VARIABLE = 8,
    CONSTANT = 9,
    BRACKET = 10,
    FUNCTOR = 11,

class ParseTree:
    """
    Stores a representation of a parse tree node. By referencing child elements, can represent a complete FTL expression.  
    
    Attributes
    ----------
    value : any
        The value of this node. 
    type : NodeType
        The type of this node.
    children : list
        A list of child ParseTree elements.
    signature: Signature
        The FTL signature over which this expression is defined.

    Methods
    -------
    isFormula()
        True if the parse tree represents an FTL formula. Otherwise False.
    isTerm()
        True if the parse tree represents an FTL term. Otherwise False.
    isAtom()
        True if the parse tree represents an FTL atom. Otherwise False.
    getVariables()
        Returns a list of all variables which appear in the entire parse tree.
    getBound()
        Returns a list of all bound variables which appear in the entire parse tree.
    getFree()
        Returns a list of all free variables which appear in the entire parse tree.
    getDomains()
        Returns a list of all domains which appear in the entire parse tree.

    """
    def __init__(self, value, type, children, signature):
        """
        Constructs a ParseTree object intialised from parameters.

        Parameters
        ----------
        value : Any
            The value taken by this node.
        type : NodeType
            The type taken by this node.
        children : list
            A list of child nodes. Should share the same signature as this node.
        signature: Signature:
            The FTL signature over which this expression is defined.
        """
        self.value = value
        self.type = type
        self.children = children
        self.signature = signature

    def __str__(self):
        """
        Returns a string representation of this parse tree.

        Returns
        -------
        : str
            A string representation of this parse tree.
        """
        currentLine = [self]
        nextLine = []
        lineno = 0
        strlst = [] #strings are immutable, so better to work with list and join at end.

        while currentLine != []:
            strlst.append("depth " + str(lineno) + ": ")
            for node in currentLine:
                if node.type == NodeType.EXISTENTIAL:
                    strlst.append(f"E{node.value[0]}~{node.value[1]}[{node.type.name}]({len(node.children)})")
                elif node.type == NodeType.UNIVERSAL:
                    strlst.append(f"A{node.value[0]}~{node.value[1]}[{node.type.name}]({len(node.children)})")
                else:    
                    strlst.append(f"{node.value}[{node.type.name}]({len(node.children)})")
                nextLine = nextLine + node.children

            currentLine = nextLine
            nextLine = []
            lineno += 1
            strlst.append("\n")
        
        return " ".join(strlst)
    
    def __eq__(self, other):
        """
        True if other is a ParseTree with equivalent properties and child nodes. Otherwise False.

        Parameters
        ----------
        other : ParseTree
            The parse tree to compare.

        Returns
        -------
        : bool
            True if other is a ParseTree with equivalent properties and child nodes. Otherwise False.
        """
        if not isinstance(other, ParseTree):
            return False
        
        if not (self.value == other.value
                and self.type == other.type
                and self.signature == other.signature):
            return False
        
        if len(self.children) != len(other.children):
            return False
        
        for i in range(0, len(self.children)):
            if not self.children[i] == other.children[i]:
                return False
        
        return True

    def isFormula(self):
        """
        True if the parse tree represents an FTL formula. Otherwise False.

        Returns
        -------
        : bool
            True if the parse tree represents an FTL formula. Otherwise False.
        """
        return self.type == NodeType.CONJUNCTION or \
               self.type == NodeType.DISJUNCTION or \
               self.type == NodeType.EXISTENTIAL or \
               self.type == NodeType.IMPLICATION or \
               self.type == NodeType.UNIVERSAL or \
               self.type == NodeType.BRACKET or \
               self.type == NodeType.NEGATION or \
               self.type == NodeType.PREDICATE
           
    def isTerm(self):
        """
        True if the parse tree represents an FTL term. Otherwise False.

        Returns
        -------
        : bool
            True if the parse tree represents an FTL term. Otherwise False.
        """
        return self.type == NodeType.CONSTANT or \
               self.type == NodeType.VARIABLE or \
               self.type == NodeType.FUNCTOR
    
    def isAtom(self):
        """
        True if the parse tree represents an FTL atom. Otherwise False.

        Returns
        -------
        : bool
            True if the parse tree represents an FTL atom. Otherwise False.
        """
        return self.type == NodeType.PREDICATE
    
    def getVariables(self):
        """
        Returns a list of all variables which appear in the entire parse tree.

        Returns
        -------
        : list
            A list of all variables which appear in the entire parse tree.
        """
        if self.type == NodeType.VARIABLE:
            return [self.value]
        elif self.type == NodeType.CONSTANT:
            return []
        else:
            vars = []
            for child in self.children:
                childVars = child.getVariables()
                for v in childVars:
                    if not v in vars:
                        vars.append(v)
            if self.type == NodeType.UNIVERSAL or self.type == NodeType.EXISTENTIAL:
                if self.value[0] not in vars:
                    vars.append(self.value[0])
            return vars
        
    def getBound(self):
        """
        Returns a list of all bound variables which appear in the entire parse tree.

        Returns
        -------
        : list
            A list of all bound variables which appear in the entire parse tree.
        """
        if self.isTerm():
            return []
        if self.type == NodeType.UNIVERSAL or self.type == NodeType.EXISTENTIAL:
            vars = self.children[0].getBound()
            vars.extend(self.value[0])
            return vars
        else:
            vars = []
            for child in self.children:
                vars.extend(child.getBound())
            return vars
        
    def getFree(self):
        """
        Returns a list of all free variables which appear in the entire parse tree.

        Returns
        -------
        : list
            A list of all free variables which appear in the entire parse tree.
        """
        return [x for x in self.getVariables() if x not in self.getBound()]
    
    def getDomains(self):
        """
        Returns a list of all domains which appear in the entire parse tree.

        Returns
        -------
        : list
            A list of all domains which appear in the entire parse tree.
        """
        if self.isTerm():
            return []
        if self.type == NodeType.UNIVERSAL or self.type == NodeType.EXISTENTIAL:
            doms = self.children[0].getDomains()
            if self.value[1] not in doms:
                doms.extend(self.value[1])
            return doms
        else:
            doms = []
            for child in self.children:
                doms.extend(child.getDomains())
            return doms


#An exception for errors when attempting to parse a formula.
class ParseError(Exception):
    pass


#The standard order of precedence for evaluating formulas.
_STANDARD_PRECEDENCE = [NodeType.BRACKET, NodeType.VARIABLE, NodeType.CONSTANT, NodeType.FUNCTOR, NodeType.PREDICATE,
                        NodeType.EXISTENTIAL, NodeType.UNIVERSAL, NodeType.NEGATION, NodeType.CONJUNCTION, NodeType.DISJUNCTION, NodeType.IMPLICATION]

#The standard junctor symbols for writing formulas.
_STANDARD_JUNCTOR_SYMBOLS = {
    NodeType.CONJUNCTION: ",",
    NodeType.DISJUNCTION: ";",
    NodeType.NEGATION: "!",
    NodeType.IMPLICATION: "-:",
}


#Finds the top level occurence of key in s.
def _findTopLevel(s, key):
    i = 0 #current position in s.
    depth = 0 #number of unmatched '(' prior to s[i].
    pos = -1 #position of key.

    while i < len(s):
        c = s[i]
        if c == ')':
            depth = max(0, depth - 1)
        if s[i:].startswith(key) and depth == 0:
            pos = i
            break
        if c == '(':
            depth += 1

        i += 1

    return pos

#Splits str at all occurences of seperator at the highest level of brackets.
def _splitAtLevel(str, seperator):
    depth = 0
    begin = 0
    result = []
    for i in range(0, len(str)):
        if str[i] == '(':
            depth += 1
        elif str[i] == ')':
            depth = max(0, depth - 1)
        elif depth == 0 and str[i:].startswith(seperator):
            result.append(str[begin:i])
            begin = i + len(seperator)
    
    result.append(str[begin:])
    return result

#Returns true if variable is a valid variable name that doesn't conflict with elements of signature.
def _varSyntaxCheck(variable, signature):
    res = re.search(r"[a-zA-Z]+[a-zA-Z0-9]*", variable)
    return (res and res.span()[0] == 0 and res.span()[1] == len(variable)
            and not variable in signature)

#Takes in a formula and a signature, and returns the parse tree of that formula.
def _parse(formula, signature, precedence, junctorSymbols):
    formula = formula.strip() #remove surrounding whitespace.
    if formula == "":
        raise ParseError("Attempting to parse an empty formula.")
    
    #Try to parse the formula as each possible type, in reverse order of precedence.
    for type in reversed(precedence):
        if type == NodeType.BRACKET:
            if formula[0] != '(':
                continue
            if formula[-1] != ')':
                raise ParseError(f"Unbalanced parenthesise in {formula}.")
            
            child = _parse(formula[1:-1], signature, precedence, junctorSymbols)
            if not child.isFormula():
                raise ParseError(f"Parenthesise surrounding non-formula {formula}.")
            return ParseTree('()', type, [child], signature)
        
        elif type == NodeType.UNIVERSAL or type == NodeType.EXISTENTIAL:
            if(type == NodeType.UNIVERSAL and formula[0] != 'A' 
               or type == NodeType.EXISTENTIAL and formula[0] != "E"):
                continue
            varEnd = formula.find('~')
            if varEnd == -1:
                continue
            
            variable = formula[1:varEnd]
            if not _varSyntaxCheck(variable, signature):
                raise ParseError(f"Quantification {formula} has invalid variable '{variable}'.")
            
            domainEnd = formula.find(':')
            if domainEnd == -1:
                raise ParseError(f"Quantification {formula} is missing ':'.")
            
            domain = formula[varEnd+1:domainEnd]
            if not _varSyntaxCheck(domain, signature):
                raise ParseError(f"Quantification {formula} has invalid domain '{domain}'.")
            
            child = _parse(formula[domainEnd+1:], signature, precedence, junctorSymbols)
            if not child.isFormula():
                raise ParseError(f"Quantification {formula} on a non-formula.")
            
            return ParseTree([variable, domain], type, [child], signature)

        elif type == NodeType.IMPLICATION or type == NodeType.DISJUNCTION or type == NodeType.CONJUNCTION:
            operatorPos = _findTopLevel(formula, junctorSymbols[type])
            if operatorPos == -1:
                continue

            children = [_parse(formula[0 : operatorPos], signature, precedence, junctorSymbols),
                        _parse(formula[operatorPos+len(junctorSymbols[type]) : ], signature, precedence, junctorSymbols)]

            if not children[0].isFormula():
                raise ParseError(f"Attempting {type} on a non-formula '{formula[0 : operatorPos]}'.")
            elif not children[1].isFormula():
                raise ParseError(f"Attempting {type} on a non-formula '{formula[operatorPos+1+len(junctorSymbols[type]) :]}'.")

            return ParseTree(junctorSymbols[type], type, children, signature)

        elif type == NodeType.NEGATION:
            if formula.startswith(junctorSymbols[NodeType.NEGATION]):
                child = _parse(formula[len(junctorSymbols[type]):], signature, precedence, junctorSymbols)
                if not child.isFormula():
                    raise ParseError(f"Attempting to negate a non-formula {formula[len(junctorSymbols[type]):]}.")
                return ParseTree(junctorSymbols[type], type, [child], signature)
            else:
                continue

        elif type == NodeType.PREDICATE or type == NodeType.FUNCTOR:
            #Get predicate or functor symbol.
            resultIndex = formula.find("(")
            if resultIndex == -1:
                continue
            symbol = formula[0 : resultIndex]

            #Check symbol is in signature and get its arity.
            arity = 0
            if type == NodeType.PREDICATE and symbol in signature.predicates:
                arity = signature.predicates[symbol]
            elif type == NodeType.FUNCTOR and symbol in signature.functors:
                arity = signature.functors[symbol]
            else:
                continue

            arguments = formula[resultIndex + 1 : -1] #returns argument string brackets.
            arguments = _splitAtLevel(arguments, ",")
            if len(arguments) != arity:
                raise ParseError(f"Symbol {symbol} has arity {arity}"+
                                 f"but received {len(arguments)} arguments in {formula}.")

            #Attempt to parse subexpressions.
            children = []
            for argument in arguments:
                #Note _parse will raise exception if parse problem arises, so we don't need to check for problems here.
                parsedArgument = _parse(argument, signature, precedence, junctorSymbols)
                #Check its children are in fact terms.
                if not parsedArgument.isTerm():
                    raise ParseError(f"Subexpression {argument}[{parsedArgument.type}] in {formula} is not a term.")
                children.append(parsedArgument)

            return ParseTree(symbol, type, children, signature)
        
        elif type == NodeType.CONSTANT:
            if formula in signature.constants:
                return ParseTree(formula, type, [], signature)
            
        elif type == NodeType.VARIABLE:            
            if _varSyntaxCheck(formula, signature):
                return ParseTree(formula, type, [], signature)
            
    #If we fall out of loop, then expression has failed to satisfy any type.    
    raise ParseError(f"Expression '{formula}' is an invalid formula.")
            

def parse(formula, signature, precedence=_STANDARD_PRECEDENCE,
          junctorSymbols=_STANDARD_JUNCTOR_SYMBOLS, onlyFormulas=False):
    """
    Returns the ParseTree representation of formula.

    Parameters
    ----------
    formula : str
        A string representation of the FTL expression.
    signature: Signature
        The signature over which formula is defined.
    precedence: list
        A compelete list of NodeType elements in decreasing order of precedence (default: standard precedence order). 
    junctorSymbols : dict
        A complete mapping of NodeType conjunction, disjunction, negation, and implication to symbols used in formula (default: standard junctor symbols).
    onlyFormulas: bool
        Raise an exception if the parsed expression is not an FTL formula (default: False).

    Returns
    -------
    : ParseTree
        A ParseTree representation of formula.
    """
    parseTree = _parse(formula, signature, precedence, junctorSymbols)
    if onlyFormulas and not parseTree.isFormula():
        raise ParseError(f"Expression {formula} is not a formula.")
    
    return parseTree