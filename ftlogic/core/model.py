"""
Create, train, and query FTL agents.

Classes:
    Model - Stores an FTL agent which can be trained and queried.
"""
import ftlogic.core as ftl
import ftlogic.fuzzyops as fops
import tensorflow as tf
from ftlogic.core.interpretation import evaluateKB
from ftlogic.core.interpretation import evaluate

class Model:
    """
    An FTL agent which can be trained and queried.
    
    Attributes
    ----------
    knowledgeBase : KnowledgeBase
        A set of formulas expressing all symbolic knowledge known to the agent.
    interpretation : Interpretation
        The agent's learnable mapping of all elements in the knowledge base.
    operatorSet : OperatorSet
        A complete set of differentiable fuzzy operators used for evaluating formula truthfulness.

    Methods
    -------
    fit(epochs, optimiser, aggregator, trainables, regulariser=None, validationKB=None):
        Train the agent to maximise its knowledge base satisfaction. Returns training history.
    query(formula):
        Returns the truthfulness of formula according to the agent.
    """
    def __init__(self, knowledgeBase, interpretation, operatorSet):
        """
        Constructs a Model object intialised from parameters.

        Parameters
        ----------
        knowledgeBase : KnowledgeBase
            A set of formulas expressing all symbolic knowledge known to the agent.
        interpretation : Interpretation
            The agent's learnable mapping of all elements in the knowledge base.
        operatorSet : OperatorSet
            A complete set of differentiable fuzzy operators used for evaluating formula truthfulness.
        """
        self.knowledgeBase = knowledgeBase
        self.interpretation = interpretation
        self.operatorSet = operatorSet

    def fit(self, epochs, optimiser, aggregator, trainables, regulariser=None,
            validationKB=None):        
        """
        Trains the agent to maximally satisfy the symbolic knowledge in its knowledge base.

        Parameters
        ----------
        epochs : int
            The number of iterations over which to train.
        optimiser : any
            An object with an apply_gradients method to update trainables from loss gradients. Accepts Keras Optimizer objects.
        aggregator: callable
            A differentiable function for aggregating batches of fuzzy truth values.
        trainables: list
            A list of references to the trainable parameters. Should be the parameters of objects mapped to by interpretation. 
        regulariser: callable, optional
            A function which accepts trainables and returns a regularisation penalty (default is None).
        validationKB : KnowledgeBase, optional
            A set of formulas whose satisfaction should be tracked during training. Not used to train the agent (default is None).

        Returns
        -------
        : dict
            A dictionary containing the loss, knowledge base satisfaction, and validation knowledge base satisfaction for each epoch.
        """
        history = {"loss": [],
                   "formula_satisfaction": [[] for _ in self.knowledgeBase],
                   "satisfaction": []}
        if validationKB:
            if validationKB.signature != self.knowledgeBase.signature:
                raise ValueError("Knowledge base signatures must match.")
            history["validation_satisfaction"] = [[] for _ in validationKB]
        
        print(f"Training model for {epochs} epochs.")
        for i in range(0, epochs):
            print(f"epoch {i + 1} / {epochs}. ", end=None)

            #Compute the loss.
            with tf.GradientTape() as tape:
                satisfaction = evaluateKB(
                    self.knowledgeBase,
                    self.interpretation,
                    self.operatorSet,
                    aggregator
                )
                loss = 1. - satisfaction
                if regulariser:
                    loss += regulariser(trainables)

            #Update trainable weights.
            gradients = tape.gradient(loss, trainables)
            optimiser.apply_gradients(zip(gradients, trainables))

            #Update history
            history["loss"].append(loss)
            for i, pt in enumerate(self.knowledgeBase.parseTrees):
                history["formula_satisfaction"][i].append(
                    evaluate(pt, self.interpretation, self.operatorSet))
            history["satisfaction"].append(satisfaction)

            if validationKB:
                for i, pt in enumerate(validationKB.parseTrees):
                    history["validation_satisfaction"][i].append(
                        evaluate(pt, self.interpretation, self.operatorSet))
                    
            #Print messages.
            print(f"loss: {loss}, ", end=None)
            print(f"satisfaction: {satisfaction}.")

        return history

    def query(self, formula):
        """
        Returns the truth value of querying the agent with formula.

        Parameters
        ----------
        formula : str, ParseTree
            A string or ParseTree representation of the query.

        Returns
        -------
        : Tensor
            A TensorFlow tensor containing the truth value of the query.
        """
        if not isinstance(formula, ftl.ParseTree):
            try:
                formula = ftl.parse(formula, 
                          self.knowledgeBase.signature)
            except Exception as err:
                raise ValueError(f"Could not parse formula {formula}. {err}")
        
        return evaluate(formula, self.interpretation, self.operatorSet)