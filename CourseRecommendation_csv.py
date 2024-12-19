import os
import csv
import sys
from surprise import Dataset
from surprise import Reader
from collections import defaultdict

class CourseRecommendation:

    courseID_to_name = {}
    name_to_courseID = {}
    courseID_to_details = {}  # Store details: difficulty_level, category_id, lecturer_id
    ratingsPath = './filtered_course_ratings.csv'
    coursesPath = './filtered_courses.csv'

    def loadCourseData(self):
        """Load course ratings dataset and course information."""
        os.chdir(os.path.dirname(sys.argv[0]))

        self.courseID_to_name = {}
        self.name_to_courseID = {}
        self.courseID_to_details = {}

        reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)

        # Load ratings dataset
        ratingsDataset = Dataset.load_from_file(self.ratingsPath, reader=reader)

        # Load course details
        with open(self.coursesPath, newline='', encoding='utf-8') as csvfile:
            courseReader = csv.reader(csvfile)
            next(courseReader)  # Skip header line
            for row in courseReader:
                courseID = row[0]  # 'id' column
                courseName = row[1]  # 'name' column
                difficulty_level = row[2]  # 'difficulty_level' column
                category_id = row[3]  # 'category_id' column
                lecturer_id = row[4]  # 'lecturer_id' column

                self.courseID_to_name[courseID] = courseName
                self.name_to_courseID[courseName] = courseID
                self.courseID_to_details[courseID] = {
                    'difficulty_level': difficulty_level,
                    'category_id': category_id,
                    'lecturer_id': lecturer_id
                }

        return ratingsDataset

    def getUserRatings(self, user):
        """Get all ratings given by a specific user."""
        userRatings = []
        hitUser = False
        with open(self.ratingsPath, newline='', encoding='utf-8') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                userID = row[0]  # 'student_id' column
                if user == userID:
                    courseID = row[1]  # 'course_id' column
                    rating = float(row[2])  # 'rating_point' column
                    userRatings.append((courseID, rating))
                    hitUser = True
                if hitUser and (user != userID):
                    break

        return userRatings

    def getPopularityRanks(self):
        """Calculate popularity ranks for courses based on the number of ratings."""
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline='', encoding='utf-8') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                courseID = row[1]  # 'course_id' column
                ratings[courseID] += 1
        rank = 1
        for courseID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[courseID] = rank
            rank += 1
        return rankings

    def getCourseName(self, courseID):
        """Get course name by its ID."""
        return self.courseID_to_name.get(courseID, "")

    def getCourseID(self, courseName):
        """Get course ID by its name."""
        return self.name_to_courseID.get(courseName, 0)

    def getDifficultyLevel(self, courseID):
        """Get difficulty level of a course by its ID."""
        return self.courseID_to_details.get(courseID, {}).get('difficulty_level', "")

    def getCategoryID(self, courseID):
        """Get category ID of a course by its ID."""
        return self.courseID_to_details.get(courseID, {}).get('category_id', "")

    def getLecturerID(self, courseID):
        """Get lecturer ID of a course by its ID."""
        return self.courseID_to_details.get(courseID, {}).get('lecturer_id', "")

# Test
if __name__ == "__main__":
    courseRecommendation = CourseRecommendation()
    dataset = courseRecommendation.loadCourseData()
    print("Dataset loaded successfully.")

    # Get popularity ranks
    print("Top 5 popular courses:", list(courseRecommendation.getPopularityRanks().items())[:5])

    # Get course name from ID
    course_name = courseRecommendation.getCourseName("c15ff891-9129-41a5-b85f-e687fc4c5213")
    print(f"Course Name: {course_name}")

    # Get course ID from name
    course_id = courseRecommendation.getCourseID("Lập trình Java Spring Boot Backend cho người mới bắt đầu")
    print(f"Course ID: {course_id}")

    # Get course details
    difficulty_level = courseRecommendation.getDifficultyLevel("c15ff891-9129-41a5-b85f-e687fc4c5213")
    category_id = courseRecommendation.getCategoryID("c15ff891-9129-41a5-b85f-e687fc4c5213")
    lecturer_id = courseRecommendation.getLecturerID("c15ff891-9129-41a5-b85f-e687fc4c5213")
    print(f"Difficulty Level: {difficulty_level}, Category ID: {category_id}, Lecturer ID: {lecturer_id}")
