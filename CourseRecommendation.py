import psycopg2
from surprise import Dataset, Reader
from collections import defaultdict
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class CourseRecommendation:
    courseID_to_name = {}
    name_to_courseID = {}
    courseID_to_details = {}  # Store details: difficulty_level, category_id, lecturer_id

    def __init__(self):
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        DB_USERNAME = os.getenv('DB_USERNAME')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_PORT = os.getenv('DB_PORT')


        self.db_config = {
        'host': DB_HOST,
        'dbname': DB_NAME,
        'user': DB_USERNAME,
        'password': DB_PASSWORD,
        'port': DB_PORT
        }

    def _connect_db(self):
        """Connect to PostgreSQL database."""
        return psycopg2.connect(**self.db_config)

    def loadCourseData(self):
        """Load course ratings dataset and course information from PostgreSQL."""
        self.courseID_to_name = {}
        self.name_to_courseID = {}
        self.courseID_to_details = {}

        connection = self._connect_db()
        cursor = connection.cursor()

        # Load ratings dataset
        cursor.execute("SELECT student_id, course_id, rating_point FROM course_ratings")
        ratings = cursor.fetchall()

        # Use Surprise's Reader to format data
        reader = Reader(line_format='user item rating timestamp', sep=',')
        ratings_df = pd.DataFrame(ratings, columns=['student_id', 'course_id', 'rating_point'])

        ratingsDataset = Dataset.load_from_df(ratings_df, reader)

        # Load course details
        cursor.execute("SELECT id, name, difficulty_level, category_id, lecturer_id FROM courses")
        courses = cursor.fetchall()

        for row in courses:
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

        cursor.close()
        connection.close()

        return ratingsDataset

    def getUserRatings(self, user):
        """Get all ratings given by a specific user from PostgreSQL."""
        userRatings = []
        connection = self._connect_db()
        cursor = connection.cursor()
        
        cursor.execute("SELECT course_id, rating_point FROM course_ratings WHERE student_id = %s", (user,))
        ratings = cursor.fetchall()

        for row in ratings:
            courseID = row[0]  # 'course_id' column
            rating = float(row[1])  # 'rating_point' column
            userRatings.append((courseID, rating))

        cursor.close()
        connection.close()
        
        return userRatings

    def getPopularityRanks(self):
        """Calculate popularity ranks for courses based on the number of ratings."""
        ratings = defaultdict(int)
        rankings = defaultdict(int)

        connection = self._connect_db()
        cursor = connection.cursor()
        
        cursor.execute("SELECT course_id FROM course_ratings")
        ratings_data = cursor.fetchall()

        for row in ratings_data:
            courseID = row[0]  # 'course_id' column
            ratings[courseID] += 1

        rank = 1
        for courseID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[courseID] = rank
            rank += 1

        cursor.close()
        connection.close()

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
    
    # Save recommend course ids to course_recommendations table
    def saveRecommendations(self, user, courses):
        connection = self._connect_db()
        cursor = connection.cursor()

        courses = ",".join(courses)

        cursor.execute("INSERT INTO course_recommendations (student_id, courses) VALUES (%s, %s) ON CONFLICT (student_id) DO UPDATE SET courses = EXCLUDED.courses", (user, courses))

        connection.commit()
        cursor.close()
        connection.close()

    # Load all users that have ratings
    def loadUsers(self):
        connection = self._connect_db()
        cursor = connection.cursor()

        cursor.execute("SELECT DISTINCT student_id FROM course_ratings")
        users = cursor.fetchall()

        cursor.close()
        connection.close()

        return users


# Example of how to use the modified class
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
