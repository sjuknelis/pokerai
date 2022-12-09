import argparse

from tree import run_tree_algorithm
from cluster import run_cluster_algorithm

parser = argparse.ArgumentParser(
  prog="PokerAI",
  description="Algorithm for calculating poker game win probabilities"
)
parser.add_argument("-v","--verbose",action="store_true",help="Verbose mode",required=False)
parser.add_argument("player_cards",help="Two cards currently in the player's hand")
parser.add_argument("--table_cards",default="",help="Up to five cards currently on the table",required=False)
parser.add_argument("--tree_descent",default="bfs",help="Algorithm used to initially descend the tree from the known game state. Default: BFS",choices=["bfs","dfs","djikstra"])
parser.add_argument("--clustering",default="kmeans",help="Algorithm used to summarize probabilities obtained from tree descent. Default: K-Means",choices=["kmeans","gd","sa","avg"])
parser.add_argument("--kmeans_clusters",default="3",help="Number of clusters for K-Means to divide the probability list into. Default: 3")
args = parser.parse_args()

probs = run_tree_algorithm(
  args.tree_descent,
  args.player_cards.split(","),
  args.table_cards.split(","),
  args.verbose
)
result = run_cluster_algorithm(
  args.clustering,
  probs,
  int(args.kmeans_clusters),
  args.verbose
)
print("Clustered results: %s" % str(result))