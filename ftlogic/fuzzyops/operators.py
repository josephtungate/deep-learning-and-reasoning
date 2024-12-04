"""
A collection of fuzzy operators.

Classes:
    OperatorSet - A complete specification of fuzzy junctors.

Methods:
    A wide variety a tnorms, snorms, and builder methods for implications and aggregators.
"""
import tensorflow as tf

#Strong negation
def strongNegation(a):
    return 1 - a

#T-norms 
def tnormGodel(a, b):
    return tf.minimum(a, b)

def tnormProduct(a, b):
    return a * b

def tnormLukasiewicz(a, b):
    return tf.maximum(a + b - 1, 0)

def tnormDrastic(a, b):
    m = tf.minimum(a, b)
    mask = tf.logical_or(tf.equal(a, 1), tf.equal(b, 1))

    return tf.where(mask, m, 0)
    
def tnormNilpotentMinimum(a, b): 
    m = tf.minimum(a, b)
    mask = tf.less_equal(a + b, 1)

    return tf.where(mask, 0, m)
    
#T-conorms (used for disjunction)
def tconorm(tnorm):
    return lambda a, b: strongNegation(tnorm(strongNegation(a), strongNegation(b)))

def tconormGodel(a, b):
    return tf.maximum(a, b)

def tconormProduct(a, b):
    return (a + b) - a * b

def tconormLukasiewicz(a, b):
    return tf.minimum(a + b, 1)

def tconormDrastic(a, b):
    m = tf.maximum(a, b)
    mask = tf.logical_or(tf.equal(a, 0), tf.equal(b, 0))

    return tf.where(mask, m, 1)
    
def tconormNilpotent(a, b):
    m = tf.maximum(a, b)
    mask = tf.greater_equal(a + b, 1)

    return tf.where(mask, 1, m)

#S-Implication
def sImplication(tconorm):
    return lambda a, c: tconorm(strongNegation(a), c)

#R-Implications
#R-implications do not have a computationally efficient way of constructing them from a tnorm.
#Therefore, define them invidivually.

def rImplicationGodel(a, c):
    mask = tf.less_equal(a, c)
    return tf.where(mask, 1., c)

def rImplicationProduct(a, c):
    mask = tf.less_equal(a, c)
    return tf.where(mask, 1., c/a)

def rImplicationLukasiewicz(a, c):
    return tf.minimum(1 - a + c, 1.)

def rImplicationDrastic(a, c):
    mask = tf.less(a, 1)
    return tf.where(mask, 1., c)

def rImplicationNilpotent(a, c):
    mask = tf.less_equal(a, c)
    return tf.where(mask, 1., tf.maximum(1 - a, c)) 
    
#Aggregators
def universalAgg(f):
    return lambda t: tf.foldl(f, t, 1.)

def existentialAgg(f):
    return lambda t: tf.foldl(f, t, 0.)

def generalisedMeanAgg(t, p):
    return tf.pow(tf.reduce_mean(tf.pow(t, p), keepdims=True), 1./p)

def generalisedMeanErrorAgg(t, p):
    return 1. - tf.pow(tf.reduce_mean(tf.pow(1. - t, p), keepdims=True), 1./p)


#Operator set for grouping operators
class OperatorSet:
    def __init__(self, negation, tnorm, tconorm, implication,
                 universal, existential, projectionEpsilon=0):
        if projectionEpsilon < 0:
            raise ValueError(f"projection epsilon must be non-negative.")
        
        if projectionEpsilon:
            incProj = lambda x : (1 - projectionEpsilon) * x + projectionEpsilon
            decProj = lambda x : (1 - projectionEpsilon) * x

            self.negation = negation
            self.tnorm = lambda a, b: tnorm(incProj(a), incProj(b))
            self.tconorm = lambda a, b: tconorm(decProj(a), decProj(b))
            self.implication = lambda a, b: implication(incProj(a), decProj(b))
            self.universal = lambda t: universal(tf.map_fn(decProj, t))
            self.existential = lambda t: existential(tf.map_fn(incProj, t))

        else:
            self.negation = negation
            self.tnorm = tnorm
            self.tconorm = tconorm
            self.implication = implication
            self.universal = universal
            self.existential = existential

#The standard product set recommended for FTL agent training.
standardProductSet = OperatorSet(strongNegation,
                        tnormProduct,
                        tconormProduct,
                        sImplication(tconormProduct),
                        lambda t: generalisedMeanErrorAgg(t, 2.),
                        lambda t: generalisedMeanAgg(t, 1.),
                        0.001)