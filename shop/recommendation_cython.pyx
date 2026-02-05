# cython: language_level=3
# distutils: language=c++

import cython
import numpy as np
cimport numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def compute_similarity_matrix(np.ndarray[np.float64_t, ndim=2] user_item_matrix):
    cdef int n_users = user_item_matrix.shape[0]
    cdef int n_items = user_item_matrix.shape[1]
    cdef np.ndarray[np.float64_t, ndim=2] similarity_matrix = np.zeros((n_items, n_items), dtype=np.float64)
    cdef np.ndarray[np.float64_t, ndim=1] item_i, item_j
    cdef double dot_product, norm_i, norm_j, similarity
    cdef int i, j
    for i in range(n_items):
        item_i = user_item_matrix[:, i]
        norm_i = np.linalg.norm(item_i)
        
        if norm_i == 0:
            continue
            
        for j in range(i, n_items):
            if i == j:
                similarity_matrix[i, j] = 1.0
                continue
                
            item_j = user_item_matrix[:, j]
            norm_j = np.linalg.norm(item_j)
            
            if norm_j == 0:
                continue
                
            dot_product = np.dot(item_i, item_j)
            similarity = dot_product / (norm_i * norm_j)
            
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity
    
    return similarity_matrix


@cython.boundscheck(False)
@cython.wraparound(False)
def predict_scores(np.ndarray[np.float64_t, ndim=1] user_ratings,
                   np.ndarray[np.float64_t, ndim=2] similarity_matrix,
                   int k=5):
    cdef int n_items = len(user_ratings)
    cdef np.ndarray[np.float64_t, ndim=1] predicted_scores = np.zeros(n_items, dtype=np.float64)
    cdef np.ndarray[np.int64_t, ndim=1] rated_items = np.where(user_ratings > 0)[0]
    cdef int i, j, count
    cdef double weighted_sum, similarity_sum, sim
    
    for i in range(n_items):
        if user_ratings[i] > 0:
            predicted_scores[i] = user_ratings[i]
            continue
            
        weighted_sum = 0.0
        similarity_sum = 0.0
        count = 0
        
        similarities = []
        for j in rated_items:
            if i != j:
                similarities.append((similarity_matrix[i, j], j))
        
        similarities.sort(reverse=True)
        top_k = similarities[:k]
        
        for sim, j in top_k:
            if sim > 0:
                weighted_sum += sim * user_ratings[j]
                similarity_sum += abs(sim)
                count += 1
        
        if similarity_sum > 0:
            predicted_scores[i] = weighted_sum / similarity_sum
    
    return predicted_scores
