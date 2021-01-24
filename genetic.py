import random as r

class Gene:
  def __init__ (self):
    self.neighbors = None
    self.embedding = None
    self.representation = None
    self.expression = None

class Chromosome:
  ALL_GENES = None
  SEQUENCE_LENGTH = 10

  def __init__ (self, sequence=None):
    self.compiled = None
    self.sequence = sequence

    if self.sequence is None:
      gs = [g for g in Chromosome.ALL_GENES.values()]
      self.sequence = [r.choice(gs) for i in range(Chromosome.SEQUENCE_LENGTH)]

  def clone (self):
    return Chromosome([g for g in self.sequence])

  def replace_genes (self, sequence):
    self.compiled = None

  def __len__ (self):
    return len(self.sequence)

  def compile (self):
    if self.compiled is not None:
      return self.compiled
    out = 0
    for i in range(len(self.sequence) - 1):
      out += abs(self.sequence[i].embedding - self.sequence[i+1].embedding)
    self.compiled = out
    return out
