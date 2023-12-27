import json
from .data_manager_interface import DataManagerInterface

class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename
    
    def get_all_users(self):
        with open(self.filename, 'r') as file:
            data = json.load(file)
            all_users = [user['name'] for user in data]
            return all_users
    
    def get_user_movies(self, user_id):
        with open(self.filename, 'r+') as file:
            data = json.load(file)

            for user in data:
                if user_id == user['id']:
                    return user['movies']
        return None

    def add_user(self, user_name):
        with open(self.filename, 'r+') as file:
            data = json.load(file)
            user_id = len(data) + 1

            new_user = {
                'id': user_id,
                'name': user_name,
                'movies': []
            }
            data.append(new_user)

            file.seek(0)
            json.dump(data, file, indent=2)
            file.truncate()

        return new_user  # Return the newly added user

    def get_max_movie_id(self):
        with open(self.filename, 'r') as file:
            data = json.load(file)

        if not data:
            return 0  # If there are no users, return 0 as the default movie ID

        max_movie_id = 0
        for user in data:
            movies = user.get('movies', [])
            if movies:
                movie_ids = [movie.get('id', 0) for movie in movies]
                max_movie_id = max(max_movie_id, max(movie_ids))

        return max_movie_id

    def add_movie(self, user_id, movie_data):
        with open(self.filename, 'r+') as file:
            data = json.load(file)

            # Check if the movie already exists in any user's list
            existing_movie = next(
                (
                    movie
                    for user in data
                    if 'movies' in user
                    for movie in user['movies']
                    if movie['name'] == movie_data['name']
                ),
                None,
            )

            if existing_movie:
                new_movie = {
                    'id': existing_movie['id'],
                    'name': movie_data['name'],
                    'poster': movie_data['poster'],
                    'director': movie_data['director'],
                    'year': movie_data['year'],
                    'rating': movie_data['rating'],
                }

                user = next((u for u in data if u['id'] == user_id), None)
                if user:
                    user.setdefault('movies', []).append(new_movie)
            else:
                # Increment the maximum movie ID to get a unique ID
                max_movie_id = self.get_max_movie_id() + 1

                new_movie = {
                    'id': max_movie_id,
                    'name': movie_data['name'],
                    'poster': movie_data['poster'],
                    'director': movie_data['director'],
                    'year': movie_data['year'],
                    'rating': movie_data['rating'],
                }

                user = next((u for u in data if u['id'] == user_id), None)
                if user:
                    user.setdefault('movies', []).append(new_movie)

            file.seek(0)
            file.truncate()
            json.dump(data, file, indent=2)

        return new_movie

    def get_user_movie(self, user_id, movie_id):
        with open(self.filename, 'r') as file:
            data = json.load(file)

        for user in data:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        return movie

        return None

    def update_movie(self, user_id, movie_id, movie_data):
        with open(self.filename, 'r+') as file:
            data = json.load(file)

        for user in data:
            if user['id'] == user_id:
                for movie in user['movies']:
                    if movie['id'] == movie_id:
                        movie['name'] = movie_data.get('name', movie['name'])
                        movie['director'] = movie_data.get('director', movie['director'])
                        movie['year'] = movie_data.get('year', movie['year'])
                        movie['rating'] = movie_data.get('rating', movie['rating'])
                        break

        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)

        return {'message': 'Movie updated successfully.'}

    def get_user_by_id(self, user_id):
        with open(self.filename, 'r') as file:
            data = json.load(file)
            for user in data:
                if user['id'] == user_id:
                    return user
        return None

    def get_movie_by_id(self, user, movie_id):
        for movie in user['movies']:
            if movie['id'] == movie_id:
                return movie
        return None

    def delete_movie(self, user_id, movie_id):
        with open(self.filename, 'r+') as file:
            data = json.load(file)

            for user in data:
                if user['id'] == user_id:
                    movies = user['movies']
                    for movie in movies:
                        if movie['id'] == movie_id:
                            movies.remove(movie)
                            break

        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)

        return {'message': 'Movie deleted successfully.'}
