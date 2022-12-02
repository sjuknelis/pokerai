import random,math

def kmeans(points,num_clusters,max_iterations):
  centroids = []
  for _ in range(num_clusters):
    centroids.append(random.random() * (max(points) - min(points)) + min(points))
  clusters = [0] * len(points)

  for _ in range(max_iterations):
    cluster_changed = False
    for (point_index,(point,current_cluster)) in enumerate(zip(points,clusters)):
      min_distance = max(points) - min(points)
      min_distance_cluster = 0
      for (cluster,centroid) in enumerate(centroids):
        if abs(centroid - point) < min_distance:
          min_distance = abs(centroid - point)
          min_distance_cluster = cluster
      if min_distance_cluster != current_cluster:
        clusters[point_index] = min_distance_cluster
        cluster_changed = True

    if not cluster_changed:
      break

    sum_adj_centroids = [0] * len(centroids)
    len_adj_centroids = [0] * len(centroids)
    for (point,cluster) in zip(points,clusters):
      sum_adj_centroids[cluster] += point
      len_adj_centroids[cluster] += 1
    for (cluster,(sum_adj,len_adj)) in enumerate(zip(sum_adj_centroids,len_adj_centroids)):
      if len_adj > 0:
        centroids[cluster] = sum_adj / len_adj

  return (centroids,clusters)

def gradient_descent(points,max_iterations):
  def total_of_dists(reference):
    total = 0
    for point in points:
      total += abs(point - reference)
    return total

  origin = random.random() * (max(points) - min(points)) + min(points)
  delta = (max(points) - min(points)) / 100
  
  for _ in range(max_iterations):
    local = total_of_dists(origin)
    ldiff = total_of_dists(origin - delta) - local
    rdiff = total_of_dists(origin + delta) - local
    if ldiff >= 0 and rdiff >= 0:
      break
    else:
      if ldiff < rdiff:
        origin -= delta
      else:
        origin += delta
  
  return (origin,total_of_dists(origin))

def simulated_annealing(points,max_iterations):
  def total_of_dists(reference):
    total = 0
    for point in points:
      total += abs(point - reference)
    return total
  def is_acceptable(diff,temperature):
    if diff < 0:
      return True
    value = pow(math.e,-diff / (0.5 * temperature))
    return value > random.random()

  origin = random.random() * (max(points) - min(points)) + min(points)
  delta = (max(points) - min(points)) / 4
  temperature = 1
  
  for _ in range(max_iterations):
    step = delta * temperature
    diff = total_of_dists(origin + step) - total_of_dists(origin)
    if is_acceptable(diff,temperature):
      origin += step
    temperature *= 0.8
  
  return (origin,total_of_dists(origin))

probs = [0.352, 0.36, 0.376, 0.378, 0.384, 0.386, 0.39, 0.394, 0.398, 0.398, 0.402, 0.408, 0.416, 0.418, 0.42, 0.436, 0.44, 0.578, 0.656, 0.658]
print(simulated_annealing(probs,10))