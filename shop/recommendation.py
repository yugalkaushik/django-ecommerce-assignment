import numpy as np
from django.db import models
from django.contrib.auth.models import User
from .models import Product, UserInteraction
from . import recommendation_cython
class RecommendationEngine:
    def __init__(self):
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.product_ids = []
        self.user_ids = []
    def build_user_item_matrix(self):
        users = User.objects.all()
        products = Product.objects.all()
        self.user_ids = [u.id for u in users]
        self.product_ids = [p.id for p in products]
        n_users = len(self.user_ids)
        n_products = len(self.product_ids)
        self.user_item_matrix = np.zeros((n_users, n_products), dtype=np.float64)
        interaction_weights = {
            'view': 1.0,
            'cart_add': 3.0,
            'like': 4.0,
            'purchase': 5.0,
            'dislike': -2.0,
        }
        interactions = UserInteraction.objects.all()
        for interaction in interactions:
            try:
                user_idx = self.user_ids.index(interaction.user_id)
                product_idx = self.product_ids.index(interaction.product_id)
                weight = interaction_weights.get(interaction.interaction_type, 1.0)
                self.user_item_matrix[user_idx, product_idx] += weight
            except ValueError:
                continue
        self.user_item_matrix = np.clip(self.user_item_matrix, 0, 5)
        return self.user_item_matrix
    def train(self):
        self.build_user_item_matrix()
        if self.user_item_matrix.size == 0:
            return
        self.similarity_matrix = recommendation_cython.compute_similarity_matrix(
            self.user_item_matrix
        )
    def get_recommendations(self, user, n_recommendations=10, exclude_interacted=True):
        if self.user_item_matrix is None or self.similarity_matrix is None:
            self.train()
        if not self.user_ids or not self.product_ids:
            return self._get_popular_products(n_recommendations)
        try:
            user_idx = self.user_ids.index(user.id)
        except ValueError:
            return self._get_popular_products(n_recommendations)
        user_ratings = self.user_item_matrix[user_idx, :].copy()
        predicted_scores = recommendation_cython.predict_scores(
            user_ratings, 
            self.similarity_matrix,
            k=10
        )
        if exclude_interacted:
            interacted_indices = np.where(user_ratings > 0)[0]
            predicted_scores[interacted_indices] = -np.inf
        top_indices = np.argsort(predicted_scores)[::-1][:n_recommendations]
        recommended_product_ids = [self.product_ids[idx] for idx in top_indices 
                                  if predicted_scores[idx] > -np.inf]
        products = Product.objects.filter(id__in=recommended_product_ids, stock__gt=0)
        product_dict = {p.id: p for p in products}
        recommended_products = [product_dict[pid] for pid in recommended_product_ids 
                               if pid in product_dict]
        if len(recommended_products) < n_recommendations:
            remaining = n_recommendations - len(recommended_products)
            popular = self._get_popular_products(remaining, 
                                                exclude_ids=[p.id for p in recommended_products])
            recommended_products.extend(popular)
        return recommended_products[:n_recommendations]
    def get_similar_products(self, product, n_similar=5):
        if self.similarity_matrix is None:
            self.train()
        try:
            product_idx = self.product_ids.index(product.id)
        except (ValueError, AttributeError):
            return list(Product.objects.filter(
                category=product.category,
                stock__gt=0
            ).exclude(id=product.id)[:n_similar])
        similarities = self.similarity_matrix[product_idx, :]
        similarities[product_idx] = -np.inf
        top_indices = np.argsort(similarities)[::-1][:n_similar]
        similar_product_ids = [self.product_ids[idx] for idx in top_indices]
        products = Product.objects.filter(id__in=similar_product_ids, stock__gt=0)
        product_dict = {p.id: p for p in products}
        return [product_dict[pid] for pid in similar_product_ids if pid in product_dict]
    def _get_popular_products(self, n=10, exclude_ids=None):
        exclude_ids = exclude_ids or []
        interactions = UserInteraction.objects.exclude(
            product_id__in=exclude_ids
        ).values('product_id').annotate(
            count=models.Count('id')
        ).order_by('-count')[:n]
        popular_ids = [i['product_id'] for i in interactions]
        products = Product.objects.filter(id__in=popular_ids, stock__gt=0)
        product_dict = {p.id: p for p in products}
        result = [product_dict[pid] for pid in popular_ids if pid in product_dict]
        if len(result) < n:
            remaining = n - len(result)
            recent = Product.objects.filter(stock__gt=0).exclude(
                id__in=exclude_ids + [p.id for p in result]
            )[:remaining]
            result.extend(list(recent))
        return result
recommendation_engine = RecommendationEngine()