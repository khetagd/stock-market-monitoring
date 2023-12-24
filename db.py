import psycopg2
from psycopg2.extras import DictCursor
import datetime

class DataBase:
    
    def __init__(self, connection):
        self.connection = connection
        
        
    def add_user(self, user_id): # добавляем пользователя в базу
        with self.connection.cursor() as cursor:
            string = f"INSERT INTO users_preferences (id) VALUES ({user_id});"
            cursor.execute(string)
            self.connection.commit()
            
    def check_user(self, user_id): # функция которая проверяет есть ли пользователь в базе
        with self.connection.cursor() as cursor:
            string = f"SELECT * FROM users_preferences WHERE id = {user_id}"
            cursor.execute(string)
            result = cursor.fetchall()
            if bool(len(result)) == False:
                self.add_user(user_id)
    
    def add_data(self, user_id, text: list):
        with self.connection.cursor() as cursor:
            select_query = f"SELECT prefs FROM users_preferences WHERE id = {user_id}"
            cursor.execute(select_query)
            existing_array = cursor.fetchone()
            if None in existing_array:
                add = f"UPDATE users_preferences SET prefs = ARRAY{text} WHERE id = {user_id}"
            else:
                updated_array = list(existing_array[0]) + list(text)
                add = f"UPDATE users_preferences SET prefs = ARRAY{updated_array} WHERE id = {user_id}"
            cursor.execute(add)
            self.connection.commit()
    
    def check_if_date_is_none(self, user_id):
        with self.connection.cursor() as cursor:
            select_query = f"SELECT last_message FROM users_preferences WHERE id = {user_id}"
            cursor.execute(select_query)
            curr_data = cursor.fetchone()
            if None in curr_data:
                date = [str(datetime.datetime.now())]
                query = f"UPDATE users_preferences SET last_message = ARRAY{date} WHERE id = {user_id}"
                cursor.execute(query)
                self.connection.commit()

    def update_date(self, user_id):
        with self.connection.cursor() as cursor:
            date = [str(datetime.datetime.now())]
            query = f"UPDATE users_preferences SET last_message = ARRAY{date} WHERE id = {user_id}"
            cursor.execute(query)
            self.connection.commit()
    
    def get_date(self, user_id):
        with self.connection.cursor() as cursor:
            select_query = f"SELECT last_message FROM users_preferences WHERE id = {user_id}"
            cursor.execute(select_query)
            curr_date = cursor.fetchone()[0].split('.')[0][2:]
            date = datetime.datetime.strptime(curr_date, '%Y-%m-%d %H:%M:%S')
            return date
    
    def get_favourites(self, user_id):
        with self.connection.cursor() as cursor:
            select_query = f"SELECT prefs FROM users_preferences WHERE id = {user_id}"
            cursor.execute(select_query)
            favs = cursor.fetchone()
            return favs
