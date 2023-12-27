from flask import Flask, redirect, request, render_template, jsonify, url_for
from data_manager.json_data_manager import JSONDataManager
import requests

app = Flask(__name__)
data_manager = JSONDataManager("movies_data.json")


@app.route('/')
def home():
  return render_template('home.html')


@app.route('/users', methods=['GET'])
def get_users():
  users = data_manager.get_all_users()
  return render_template('users.html', users=users)

@app.route('/user/<int:user_id>/movies', methods=['GET'])
def display_user_movies(user_id):
  user_movies = data_manager.get_user_movies(user_id)
  if user_movies is None:
    return "User not found.", 404
  return render_template("user_movies.html", user_movies=user_movies, user_id=user_id)


@app.route('/user_movies/<user_id>', methods=['GET'])
def get_user_movies(user_id):
    try:
        # Attempt to convert the user_id to an integer
        user_id = int(user_id)
    except ValueError:
        return "Invalid user ID.", 400  # Return a 400 Bad Request status for invalid IDs
    
    user_movies = data_manager.get_user_movies(user_id)
    user = data_manager.get_user_by_id(user_id)
    
    if user_movies is None or user is None:
        return "User not found.", 404
    
    return render_template("user_movies.html", user=user, user_movies=user_movies)




@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        user_name = request.form.get('name')

        if not user_name:
            return jsonify({'error': 'User name is missing.'}), 400

        # Check if the user already exists
        users = data_manager.get_all_users()
        if user_name in users:
            return jsonify({'error': 'User already exists.'}), 409

        new_user = data_manager.add_user(user_name)
        return redirect(url_for("get_users", new_user=new_user))

    # Handle GET request
    return render_template("add_user.html")

# OMDb API base URL
OMDB_API_URL = "http://www.omdbapi.com/"
OMDB_API_KEY = "770a6d70"

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
  if request.method == 'POST':
    # Check if the user exists
    user_movies = data_manager.get_user_movies(user_id)
    user = data_manager.get_user_by_id(user_id)
    user_name = user.get('name', 'Unknown') if user else 'Unknown'

    if user_movies is None:
      return jsonify({'error': 'User not found'}), 404

    # Extract the movie data from the request's form
    movie_data = request.form.to_dict()
    if not movie_data:
      return jsonify({'error': 'No movie data provided'}), 400
    
    # Extract the movie name from the form data
    movie_name = movie_data.get('name')
    
    # Fetch movie details from OMDb API
    omdb_params = {'t': movie_name, 'apikey': OMDB_API_KEY}
    omdb_response = requests.get(OMDB_API_URL, params=omdb_params)
    omdb_data = omdb_response.json()

    if omdb_response.status_code == 200 and omdb_data['Response'] == 'True':
      # Extract relevant movie details from OMDb API response
      movie_data['poster'] = omdb_data.get('Poster', 'N/A')
      movie_data['director'] = omdb_data.get('Director', 'N/A')
      movie_data['year'] = omdb_data.get('Year', 'N/A')
      movie_data['rating'] = omdb_data.get('imdbRating', 'N/A')

      # Add the movie to the user's list
      new_movie = data_manager.add_movie(user_id, movie_data)

      if new_movie is None:
            return jsonify({'error': 'Failed to add movie to user.'}), 500
      
      # Pass the newly added movie data and user_name to the template for display
      return redirect(url_for('get_user_movies', user_id=user_id))

    else:
      # Add the movie to the user's list
      new_movie = data_manager.add_movie(user_id, movie_data)
    if new_movie is None:
      return jsonify({'error': 'Failed to add movie to user.'}), 500

    # Pass the newly added movie data and user_name to the template for display
    return redirect(url_for('get_user_movies', user_id=user_id))
  else:
    # If the request is GET, render the template for adding a movie
    user = data_manager.get_user_by_id(user_id)
    user_name = user.get('name', 'Unknown') if user else 'Unknown'  
    return render_template('add_movie.html', user_id=user_id, user_name=user_name, movie_exist=None,
                           new_movie=None)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST', 'PUT'])
def update_movie(user_id, movie_id):
  if request.method == 'GET':
    # Retrieve the movie details from the data manager and pass them to the template
    movie = data_manager.get_user_movie(user_id, movie_id)
    return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie=movie)

  elif request.method == 'POST' or request.method == 'PUT':
    movie_data = request.form.to_dict()
    result = data_manager.update_movie(user_id, movie_id, movie_data)
    if 'message' in result and result['message'] == 'Movie updated successfully.':
      # If the movie was successfully updated, retrieve the updated movie details
      updated_movie = data_manager.get_user_movie(user_id, movie_id)
      return redirect(url_for('get_user_movies', user_id=user_id))


    # If the movie update failed, display an error message or handle the error scenario here
    return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie=None, updated=False)

  else:
    # Handle other methods if needed
    return "Method Not Allowed", 405


# Add the method_override route
@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['POST'])
def update_movie_method_override(user_id, movie_id):
  if request.form.get('_method') == 'PUT':
    # Treat the request as a PUT request
    return update_movie(user_id, movie_id)

  # Return a 405 Method Not Allowed status for other methods
  return '', 405


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
  user = data_manager.get_user_by_id(user_id)
  if user:
    movie = data_manager.get_movie_by_id(user, movie_id)
    if movie:
      if request.method == 'POST':
        result = data_manager.delete_movie(user_id, movie_id)
        return redirect(url_for('get_user_movies', user_id=user_id))
        
      return render_template('delete_movie.html', user=user, movie=movie)
  return "User or movie not found.", 404


@app.errorhandler(404)
def page_not_found():
  return render_template('404.html'), 404


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=5000)

