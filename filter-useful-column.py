import pandas as pd

# Đọc file gốc
rating_org = pd.read_csv('./course_ratings.csv')

rating_filtered_data = rating_org[['student_id', 'course_id', 'rating_point', 'create_at']]

# Lưu file mới để dùng với Surprise
rating_filtered_data.to_csv('./filtered_course_ratings.csv', index=False)


course_org = pd.read_csv('./courses.csv')
coure = course_org[['id', 'name', 'difficulty_level', 'category_id', 'lecturer_id']].drop_duplicates()
coure.to_csv('./filtered_courses.csv', index=False)