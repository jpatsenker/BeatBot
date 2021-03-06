import random as r
import json

import discriminator

# x, our instance variable, is the set of genes that can be combined to form
#  a chromosome
# m is our objective function, generally the same as Fg in unconstrainted
#   optimization problems, but not in constrained optimization problems,
#   nor in decision problems
# sol is the set of sequences of gemes which pass some filtering criteria to
#     be considered to form a valid chromosome
# ans is the set of all sequences of genes (within some set length-bounds)
# S is our search space, a subset of ans with the property that at least one
#   optimal element of sol is present
# N, our neighborhood function, represents a transformation from one element of
#   S to another. A graph built from this function should be connected.
# Fg, our guiding function, maps elements of ans to F (the fitness values) and
#   is able to produce a consistent ordering of the elemnts of F. Note that in
#   the case where sol and ans are the same, F may need to produce an evaluation
#   for some elements of ans which m doesn't need to include in its domain

# In our case,
# x will be a set of short clips from our library (lofibrary).
# m and Fg will be the same function which will be a descriminator that attempts
#   to classify a clip as either generated by the genetic algorithm or taken
#   from the lofibrary
# sol and ans will be the same set, but we might change that in the future (in
#   which case we may need to create a new m). We will set fixed clip length of
#   9 seconds
# N will be a function that mutates one gene. We can constrain it to only allow
#   mutations from one clip to another when their embeddings are within some
#   maximum distance of each other

def N (c):
  c = c.clone()

  # index to mutate
  i = r.randrange(len(c))
  c.sequence[i] = r.choice(c.sequence[i].neighbors)

  return c

# mutate several genes at once
def N_it (c, MIN_MUTATIONS, MAX_MUTATIONS):
  c = c.clone()

  # indices to mutate
  to_mutate = [i for i in range(len(c))]
  r.shuffle(to_mutate)

  num_mutations = r.randrange(MAX_MUTATIONS - MIN_MUTATIONS) + MIN_MUTATIONS
  to_mutate = to_mutate[:num_mutations]

  for i in to_mutate:
    c.sequence[i] = r.choice(c.sequence[i].neighbors)

  return c

# Note: want to normalize this to always have fitness > 0
def Fg (c):
  if c.compiled is None:
    c.compile()

  fitness = discriminator.check(c.compiled)
  return fitness

# Have the algorithm's primitive functions, now combine them to define search

LOCAL_SEARCH_GENERATIONS = 30
def local_search (current):
  # local search performs a fixed number of mutations asexually and keeps the
  #   resulting mutations which are beneficial to fitness
  terminate = False
  generation = 0
  while not terminate:
    next = mutate_individual(current)

    if Fg(next) > Fg(current):
      current = next

    if generation > LOCAL_SEARCH_GENERATIONS:
      terminate = True
    generation += 1

  return current

# Used for local search
def mutate_individual (individual):
  return N(individual)

# This algorithm is very progressive because it allows any number of parents
def mate_individuals (*parents):
  total = sum([Fg(parent) for parent in parents]) + 1

  child_seq = []
  most_fit_parent = None
  most_fitness = -1

  for parent in parents:
    fitness = Fg(parent)
    if fitness > most_fitness:
      most_fitness = fitness
      most_fit_parent = parent

  i = 0
  done = False

  # Note: this crossover function relies on it not making a big difference to
  #   round fitness values to integers
  while not done:
    which = r.randrange(total)

    # Scale the likelihood of inheriting a gene from a given parent by the
    #   fitness of that parent. You can probably do this more efficiently with
    #   like math and getting the index that way
    # May want to experiment with other methods for recombination in cases where
    #   you want to keep some continuity from one gene to the next (for example)
    for parent in parents:
      if which - fitness <= 0:
        if i >= len(parent.sequence):
          done = True
        else:
          child_seq.append(parent.sequence[i])
          i += 1
          break
      else:
        which -= fitness

  child = parents[0].clone()
  child.replace_genes(child_seq)
  return child

CULLING_PERCENT = 0.5
def op_selection (pop):
  # Note: may want to incorporate some randomness into culling
  new_size = int(len(pop) * CULLING_PERCENT)
  return sorted(pop, key=Fg, reverse=True)[:new_size]

def op_recombination (pop):
  # For now, no sexual selection (i.e. completely random mating)
  number_children = len(pop) * 2
  children = []

  # TODO: multiprocessing
  for i in range(number_children):
    # Note: there is a chance that both parents are the same individual
    children.append(mate_individuals(r.choice(pop), r.choice(pop)))
  return pop + children

def op_local_search (pop):
  # TODO: multiprocessing
  for i in range(len(pop)):
    pop.append(local_search(pop[i]))
  return pop

# Note: the difference between mutation and local search is that mutation can
#       decrease fitness
def op_mutation (pop):
  # TODO: multiprocessing
  for i in range(len(pop)):
    pop[i] = mutate_individual(pop[i])
  return pop

OPS = [op_selection, op_recombination, op_local_search, op_mutation, op_local_search]
# Selection ->  halve population
# Recombination -> triple population
# Local_search -> double population
# Mutation -> same population size
# Local_search -> double population
def generate_new_population (pop):
  for op in OPS:
    S_ancestors = clone_population(pop)
    S_descendants = op(S_ancestors)
    pop = S_descendants

  return pop

def clone_population (pop):
  # Deep copy each individual
  return [individual.clone() for individual in pop]

def update_population (pop, new_pop, MAX_POP_SIZE=None):
  # new_pop is large compared to pop_size, therefore we can select updates only
  #   from new_pop. Alternative is to take randomly from pop U new_pop
  updated_population = sorted(new_pop, key=Fg, reverse=True)
  if MAX_POP_SIZE is not None:
    updated_population = updated_population[:MAX_POP_SIZE]
  return updated_population

ENTROPY = 0 # Shannon's entropy of the population
# TODO: implement this if needed
def has_converged (pop):
  # Calculate Shannon's entropy for the lexicon of this population and compare
  #   it to the (known) entropy of a random population
  return False

def restart_population (pop):
  # Keep the most fit individual of the degenerate population, then fill the
  #   rest of the population with randos
  # Note: don't want this fit individual to be an invasive species. possible
  #   solution is to have lower selective pressure the first generation after a
  #   restart
  out = generate_new_population()
  out.pop()
  out.append(pop[0])
  return out
