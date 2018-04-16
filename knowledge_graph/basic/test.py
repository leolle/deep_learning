# -*- coding: utf-8 -*-
import pandas as pd
from py2neo import Node, Relationship, size, order, Graph, NodeSelector
import pandas as pd

graph = Graph('http://127.0.0.1:7474')
a = Node('Person', name='Alice')
b = Node('Person', name='Bob')
r = Relationship(a, 'KNOWS', b)

print(a,b,r)
s = a|b|r
graph.create(s)

data = graph.data('MATCH (n:Person) RETURN n.name')
print(data)
