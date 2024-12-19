from surprise import AlgoBase
from surprise import PredictionImpossible
import numpy as np
import heapq

class ContentKNNAlgorithm(AlgoBase):

    def __init__(self, k=40, sim_options={}, courseRecommendation=None):
        super().__init__()
        self.k = k
        self.courseRecommendation = courseRecommendation

    def fit(self, trainset):
        super().fit(trainset)

        # Compute item similarity matrix based on course attributes
        print("Computing content-based similarity matrix...")

        self.similarities = np.zeros((self.trainset.n_items, self.trainset.n_items))

        for thisRating in range(self.trainset.n_items):
            if thisRating % 100 == 0:
                print(thisRating, " of ", self.trainset.n_items)

            for otherRating in range(thisRating + 1, self.trainset.n_items):
                thisCourseID = self.trainset.to_raw_iid(thisRating)
                otherCourseID = self.trainset.to_raw_iid(otherRating)

                # Calculate similarity based on custom attributes
                similarity = self.computeSimilarity(thisCourseID, otherCourseID)
                self.similarities[thisRating, otherRating] = similarity
                self.similarities[otherRating, thisRating] = similarity

        print("...done.")
        return self

    def computeSimilarity(self, course1, course2):
        """Calculate similarity between two courses based on attributes."""
        if not self.courseRecommendation:
            raise ValueError("CourseRecommendation instance is required to compute similarity.")

        details1 = self.courseRecommendation.courseID_to_details.get(course1, {})
        details2 = self.courseRecommendation.courseID_to_details.get(course2, {})

        # Extract attributes
        difficulty1 = details1.get('difficulty_level', '')
        difficulty2 = details2.get('difficulty_level', '')
        category1 = details1.get('category_id', '')
        category2 = details2.get('category_id', '')
        lecturer1 = details1.get('lecturer_id', '')
        lecturer2 = details2.get('lecturer_id', '')

        # Compute similarity (example logic: assign weights to matching attributes)
        similarity = 0
        if difficulty1 == difficulty2:
            similarity += 0.4  # 40% weight for matching difficulty level
        if category1 == category2:
            similarity += 0.4  # 40% weight for matching category
        if lecturer1 == lecturer2:
            similarity += 0.2  # 20% weight for matching lecturer

        return similarity

    def estimate(self, u, i):
        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unknown.')

        # Build up similarity scores between this item and everything the user rated
        neighbors = []
        for rating in self.trainset.ur[u]:
            similarity = self.similarities[i, rating[0]]
            neighbors.append((similarity, rating[1]))

        # Extract the top-K most-similar ratings
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[0])

        # Compute average sim score of K neighbors weighted by user ratings
        simTotal = weightedSum = 0
        for (simScore, rating) in k_neighbors:
            if simScore > 0:
                simTotal += simScore
                weightedSum += simScore * rating

        if simTotal == 0:
            raise PredictionImpossible('No neighbors')

        predictedRating = weightedSum / simTotal

        return predictedRating
