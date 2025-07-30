import abc

from pyowl2.abstracts.axiom import OWLAxiom


class OWLObjectPropertyAxiom(OWLAxiom, abc.ABC, metaclass=abc.ABCMeta):
    """An axiom defining relationships or characteristics of object properties."""

    __slots__ = ()
