import psycopg2
from psycopg2.extras import DictCursor

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
                