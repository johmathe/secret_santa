#!/usr/bin/python
# Author: Johan Mathe (johmathe@acm.org)

"""A script to solve the secret santa problem and send results.

The problem is being solved by using a cardinality-matching algorithm on top of
a bipartite graph. Complexity is O(N^2) with N number of attendees.

If a list of couples is defined, these won't exchange gifts.
"""

import os
import random

g_attendees = { 'babeth'  : 'replaceme@google.com',
                'claude'  : 'replaceme@google.com',
                'johan'   : 'replaceme@google.com',
                'julia'   : 'replaceme@google.com',
                'louise'  : 'replaceme@google.com',
                'morgane' : 'replaceme@google.com',
                'tom'     : 'replaceme@google.com' }

g_couples = [ ('johan', 'louise') ]

SENDMAIL_PATH = '/usr/sbin/sendmail'


# Hopcroft-Karp bipartite max-cardinality matching and max independent set
# David Eppstein, UC Irvine, 27 Apr 2002
def BipartiteMatch(graph):
  """Find maximum cardinality matching of a bipartite graph (U,V,E).
  The input format is a dictionary mapping members of U to a list
  of their neighbors in V. The output is a triple (M,A,B) where M is a
  dictionary mapping members of V to their matches in U, A is the part
  of the maximum independent set in U, and B is the part of the MIS in V.
  The same object may occur in both U and V, and is treated as two
  distinct vertices if this happens."""

  # initialize greedy matching (redundant, but faster than full search)
  matching = {}
  for u in graph:
    for v in graph[u]:
      if v not in matching:
        matching[v] = u
        break

  while 1:
    # structure residual graph into layers
    # pred[u] gives the neighbor in the previous layer for u in U
    # preds[v] gives a list of neighbors in the previous layer for v in V
    # unmatched gives a list of unmatched vertices in final layer of V,
    # and is also used as a flag value for pred[u] when u is in the first layer
    preds = {}
    unmatched = []
    pred = dict([(u,unmatched) for u in graph])
    for v in matching:
      del pred[matching[v]]
    layer = list(pred)

    # repeatedly extend layering structure by another pair of layers
    while layer and not unmatched:
      new_layer = {}
      for u in layer:
        for v in graph[u]:
          if v not in preds:
            new_layer.setdefault(v, []).append(u)
      layer = []
      for v in new_layer:
        preds[v] = new_layer[v]
        if v in matching:
          layer.append(matching[v])
          pred[matching[v]] = v
        else:
          unmatched.append(v)

    # did we finish layering without finding any alternating paths?
    if not unmatched:
      unlayered = {}
      for u in graph:
        for v in graph[u]:
          if v not in preds:
            unlayered[v] = None
      return (matching,list(pred),list(unlayered))

    # recursively search backward through layers to find alternating paths
    # recursion returns true if found path, false otherwise
    def Recurse(v):
      if v in preds:
        L = preds[v]
        del preds[v]
        for u in L:
          if u in pred:
            pu = pred[u]
            del pred[u]
            if pu is unmatched or Recurse(pu):
              matching[v] = u
              return 1
      return 0

    for v in unmatched: Recurse(v)


def CreateBigraph(attendees, couples):
  g = {}
  randomized_attendees = attendees.keys()
  random.shuffle(randomized_attendees)
  for p1 in attendees.iterkeys():
    for p2 in randomized_attendees:
      if p1 is p2 or (p1, p2) in couples or (p2, p1) in couples:
        continue
      g.setdefault(p1, []).append(p2)
  return g


def SendEmail(subject, body, dest):
  """Sends an email to the destination address."""
  p = os.popen('%s -t' % SENDMAIL_PATH, 'w')
  p.write('To: %s\n' % dest)
  p.write('Subject: %s\n' % subject)
  p.write('\n')
  p.write('%s' % body)
  p.write('\n\nYours friendly, the secret santa generator')
  p.close()


def MakeSureEverybodyHasGift(attendees_mapping):
  attendees = attendees_mapping.copy()
  while attendees:
    count = 1
    root = attendees.keys()[0]
    a = attendees[root]
    while a is not root:
      a = attendees.pop(a)
      count += 1
    print 'Cycle with %d people' % count
    attendees.pop(a)


def main():
  assert(len(g_attendees) > 1)
  graph = CreateBigraph(g_attendees, g_couples)
  (attendees_mapping, b, c) = BipartiteMatch(graph)
  MakeSureEverybodyHasGift(attendees_mapping)
  for recipient in attendees_mapping:
    body = 'Hi %s, your match is %s' % (recipient,
                                        attendees_mapping[recipient])
    subject = 'Your secret santa match!'
    SendEmail(subject, body, g_attendees[recipient])

if __name__ == '__main__':
  main()
