from CourseRecommendation import CourseRecommendation
from RBMAlgorithm import RBMAlgorithm
from ContentKNNAlgorithm import ContentKNNAlgorithm
from HybridAlgorithm import HybridAlgorithm
from Evaluator import Evaluator

import random
import numpy as np

def LoadCourseData():
    coursesData = CourseRecommendation()
    print("Loading movie ratings...")
    data = coursesData.loadCourseData()
    print("\nComputing movie popularity ranks so we can measure novelty later...")
    rankings = coursesData.getPopularityRanks()
    users = coursesData.loadUsers()
    return (coursesData, data, rankings, users)
    

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(coursesData, evaluationData, rankings, users) = LoadCourseData()

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

#Simple RBM
SimpleRBM = RBMAlgorithm(epochs=40)
#Content
ContentKNN = ContentKNNAlgorithm(10, {}, coursesData)

#Combine them
Hybrid = HybridAlgorithm([SimpleRBM, ContentKNN], [0.5, 0.5])

evaluator.AddAlgorithm(SimpleRBM, "RBM")
evaluator.AddAlgorithm(ContentKNN, "ContentKNN")
evaluator.AddAlgorithm(Hybrid, "Hybrid")

# Fight!
evaluator.Evaluate(False)

# Sample top-10 recommendations for each user

print("\nUser sample recommendations:")
print(users)

for user in users:
    print("\nUser: ", user[0])
    evaluator.SampleTopNRecs(coursesData, testSubject=user[0])

# evaluator.SampleTopNRecs(coursesData, "ea51fc33-82a2-4e55-9c86-a7a9ea73413b")
