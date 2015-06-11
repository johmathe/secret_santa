# SecretSanta

A script to solve the secret santa problem and send results.
The problem is being solved by using a cardinality-matching algorithm on top of
a bipartite graph. Complexity is O(N^2) with N number of attendees.
If a list of couples is defined, these won't exchange gifts.
