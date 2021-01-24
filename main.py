from memetic import *
import genetic

# Setup genes
all_gene_reps = list('qwertyuiopasdfghjklzxcvbnm')
genetic.Chromosome.ALL_GENES = dict()
for rep in all_gene_reps:
  gene = genetic.Gene()
  gene.representation = rep
  gene.expression = rep

  genetic.Chromosome.ALL_GENES[rep] = gene

# Get embeddings
for rep, gene in genetic.Chromosome.ALL_GENES.items():
  gene.embedding = ord(rep)-96

# Track neighbors
# TODO: may want to do this in a way that isn't the least efficient conceivable
for rep1, gene1 in genetic.Chromosome.ALL_GENES.items():
  if gene1.neighbors is not None:
    continue

  gene1.neighbors = []
  for rep2, gene2 in genetic.Chromosome.ALL_GENES.items():
    if gene1 is gene2:
      continue
    if abs(gene1.embedding - gene2.embedding) < 3:
      gene1.neighbors.append(gene2)

### The meat and potatoes ###
GENERATIONS = 3
POP_SIZE = 100
def population_based_search ():
  # Generate initial population
  pop = []
  for i in range(POP_SIZE):
    c = genetic.Chromosome(None) # pass None to get a random gene sequence
    c = local_search(c)
    pop.append(c)

  for i in range(GENERATIONS):
    print('Generation', i)
    new_pop = generate_new_population(pop)
    pop = update_population(pop, new_pop, POP_SIZE)

    if has_converged(pop):
      pop = restart_population(pop)
      # i = 0

    REPORT_EVERY = 1
    if i % REPORT_EVERY == 0:
      out_pop = [''.join([g.representation for g in c.sequence]) for c in pop]
      out_pop = sorted(out_pop, reverse=True)

      with open('out/' + str(i) + '.json', 'w') as file:
        file.write(json.dumps(out_pop, indent=2, ensure_ascii=False))

  return pop


# Create initial population
pop = population_based_search()
for i in pop:
  i.compile()

out_pop = [''.join([g.representation for g in c.sequence]) for c in pop]
out_pop = sorted(out_pop, reverse=True)

with open('out/final.json', 'w') as file:
  file.write(json.dumps(out_pop, indent=2, ensure_ascii=False))
