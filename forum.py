import uuid
import json
import datetime
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Database Configuration ---
# IMPORTANT: Replace these with your actual MySQL database credentials.
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "leetflix"

# --- SQL Schema ---
# Run these SQL commands in your MySQL database to create the necessary tables.
# CREATE TABLE posts (
#     id VARCHAR(36) PRIMARY KEY,
#     series VARCHAR(255) NOT NULL,
#     title VARCHAR(255) NOT NULL,
#     content TEXT NOT NULL,
#     author_id VARCHAR(255) NOT NULL,
#     timestamp DATETIME NOT NULL
# );

# CREATE TABLE comments (
#     id VARCHAR(36) PRIMARY KEY,
#     post_id VARCHAR(36) NOT NULL,
#     content TEXT NOT NULL,
#     author_id VARCHAR(255) NOT NULL,
#     timestamp DATETIME NOT NULL,
#     FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
# );

# CREATE TABLE votes (
#     id VARCHAR(36) PRIMARY KEY,
#     post_id VARCHAR(36) NOT NULL,
#     user_id VARCHAR(255) NOT NULL,
#     vote_type VARCHAR(10) NOT NULL, -- 'upvote' or 'downvote'
#     UNIQUE KEY (post_id, user_id),
#     FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
# );

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# --- HTML Content ---
# This serves the complete frontend, including HTML, CSS, and JavaScript.
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeetFlix Discussions</title>
    <!-- Tailwind CSS from CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #161723;
            color: #f0f4f8;
            min-height: 100vh;
        }

        .no-scroll {
            overflow: hidden;
        }

        /* Custom scrollbar for better aesthetics */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1e1f2b;
        }

        ::-webkit-scrollbar-thumb {
            background: #4a4b5d;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #6c6d83;
        }
    </style>
    <script>
        // The URL for your Flask backend. This must be running for the app to work.
        const API_URL = ''; 
        
        // Define the administrator ID
        const ADMIN_ID = 'admin-1234';
        
        // Check for admin URL parameter to determine the user ID
        const urlParams = new URLSearchParams(window.location.search);
        const userId = urlParams.get('admin') ? ADMIN_ID : 'user_' + Math.random().toString(36).substr(2, 9);
        
        document.addEventListener('DOMContentLoaded', () => {
            if (userId === ADMIN_ID) {
                document.getElementById('userIdDisplay').textContent = `Logged in as: Administrator`;
                document.getElementById('userIdDisplay').classList.add('text-[#e50914]');
            } else {
                document.getElementById('userIdDisplay').textContent = `User ID: ${userId}`;
            }
            initApp();
        });

        const seriesList = ['Stranger Things', 'Friends', 'Modern Family', 'Squid Game', 'Breaking Bad'];
        const state = {
            currentSeries: null,
            isModalOpen: false,
        };

        function showMessage(message) {
            const messageBox = document.getElementById('messageBox');
            messageBox.textContent = message;
            messageBox.classList.remove('hidden');
            setTimeout(() => {
                messageBox.classList.add('hidden');
            }, 3000);
        }

        function initApp() {
            const seriesContainer = document.getElementById('seriesList');
            seriesList.forEach(seriesName => {
                const button = document.createElement('a');
                button.href = '#';
                button.textContent = seriesName;
                button.className = 'series-btn block p-4 rounded-lg shadow-inner transition-colors duration-200 transform hover:scale-[1.01] font-medium';
                button.dataset.series = seriesName;
                button.onclick = () => {
                    selectSeries(seriesName);
                };
                seriesContainer.appendChild(button);
            });
            // Automatically select the first series
            if (seriesList.length > 0) {
                selectSeries(seriesList[0]);
            }

            document.getElementById('addPostBtn').onclick = toggleModal;
            document.getElementById('closeModalBtn').onclick = toggleModal;
            document.getElementById('postForm').onsubmit = handlePostSubmit;
        }
        
        function selectSeries(seriesName) {
            // Remove highlight from all buttons and reset their classes
            document.querySelectorAll('.series-btn').forEach(btn => {
                btn.classList.remove('bg-[#e50914]', 'hover:bg-[#e50914]');
                btn.classList.add('bg-gray-800', 'hover:bg-gray-700');
            });
            
            // Add highlight to the selected button
            const selectedBtn = document.querySelector(`.series-btn[data-series="${seriesName}"]`);
            if (selectedBtn) {
                selectedBtn.classList.remove('bg-gray-800', 'hover:bg-gray-700');
                selectedBtn.classList.add('bg-[#e50914]', 'hover:bg-[#e50914]');
            }

            state.currentSeries = seriesName;
            document.getElementById('discussionTitle').textContent = `Discussions for ${seriesName}`;
            document.getElementById('postsContainer').innerHTML = '<p class="text-center text-gray-400">Loading discussions...</p>';
            loadPosts(seriesName);
        }

        function toggleModal() {
            state.isModalOpen = !state.isModalOpen;
            const modal = document.getElementById('postModal');
            if (state.isModalOpen) {
                modal.classList.remove('hidden');
                document.body.classList.add('no-scroll');
            } else {
                modal.classList.add('hidden');
                document.body.classList.remove('no-scroll');
            }
        }

        async function handlePostSubmit(event) {
            event.preventDefault();

            const form = event.target;
            const title = form.elements['postTitle'].value;
            const content = form.elements['postContent'].value;

            if (!title || !content || !state.currentSeries) {
                showMessage('Please fill out all fields.');
                return;
            }

            const newPost = {
                series: state.currentSeries,
                title: title,
                content: content,
                authorId: userId,
            };
            
            try {
                const response = await fetch(`${API_URL}/posts`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newPost)
                });

                if (response.ok) {
                    form.reset();
                    toggleModal();
                    loadPosts(state.currentSeries);
                } else {
                    showMessage('Failed to post discussion.');
                }
            } catch (error) {
                console.error('An error occurred:', error);
                showMessage('An error occurred. Could not post discussion. Make sure your backend is running.');
            }
        }

        async function handlePostDelete(postId) {
            try {
                const response = await fetch(`${API_URL}/posts/${postId}?user_id=${userId}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    loadPosts(state.currentSeries);
                } else {
                    showMessage('Failed to delete post.');
                }
            } catch (error) {
                console.error('An error occurred:', error);
                showMessage('An error occurred. Could not delete post. Make sure your backend is running.');
            }
        }

        async function loadPosts(seriesName) {
            const postsContainer = document.getElementById('postsContainer');
            postsContainer.innerHTML = '<p class="text-center text-gray-400">Loading discussions...</p>';
            
            try {
                const response = await fetch(`${API_URL}/posts/${seriesName}`);
                if (!response.ok) throw new Error('Failed to fetch posts');
                
                const posts = await response.json();
                postsContainer.innerHTML = '';
                
                if (posts.length === 0) {
                    postsContainer.innerHTML = '<p class="text-center text-gray-400">No discussions yet. Be the first to post!</p>';
                    return;
                }

                posts.forEach((post) => {
                    const postElement = createPostElement(post);
                    postsContainer.appendChild(postElement);
                });

            } catch (error) {
                postsContainer.innerHTML = `<p class="text-center text-[#e50914]">Error loading discussions. Make sure the Flask backend is running.</p>`;
            }
        }

        function createPostElement(post) {
            const postDiv = document.createElement('div');
            postDiv.className = 'bg-gray-800 p-6 rounded-lg shadow-lg space-y-4';

            let postDeleteButton = '';
            if (userId === ADMIN_ID || post.authorId === userId) {
                 postDeleteButton = `
                     <button class="text-gray-400 hover:text-[#e50914] transition-colors duration-200" onclick="handlePostDelete('${post.id}')">
                         <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-[#e50914]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-9V4a1 1 0 00-1-1H9a1 1 0 00-1 1v3m.75 0h8.5" />
                         </svg>
                     </button>
                 `;
            }

            // Post content
            postDiv.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-2xl font-bold text-[#e50914]">${post.title}</h3>
                        <p class="text-sm text-gray-500">by ${post.authorId} - ${new Date(post.timestamp).toLocaleDateString()}</p>
                    </div>
                    <!-- Voting system & Admin Delete -->
                    <div class="flex items-center space-x-2">
                        ${postDeleteButton}
                        <button class="upvote-btn text-gray-400 ${post.upvotes.includes(userId) ? 'text-[#e50914]' : 'hover:text-[#e50914]'} transition-colors duration-200" data-id="${post.id}">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                            </svg>
                        </button>
                        <span class="text-sm font-semibold text-gray-300">${post.upvotes.length}</span>
                        <button class="downvote-btn text-gray-400 ${post.downvotes.includes(userId) ? 'text-[#e50914]' : 'hover:text-[#e50914]'} transition-colors duration-200" data-id="${post.id}">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                        <span class="text-sm font-semibold text-gray-300">${post.downvotes.length}</span>
                    </div>
                </div>
                <p class="text-gray-300">${post.content}</p>
                <div class="comments-section space-y-2 border-t border-gray-700 pt-4">
                    <h4 class="text-md font-bold">Comments</h4>
                    <div id="comments-${post.id}" class="space-y-2"></div>
                    <form class="comment-form flex space-x-2" data-id="${post.id}">
                        <input type="text" name="commentContent" placeholder="Write a comment..." class="flex-grow p-2 rounded-lg bg-gray-700 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#e50914]">
                        <button type="submit" class="bg-[#e50914] hover:bg-[#e50914] text-white font-bold p-2 rounded-lg transition-colors duration-200">Comment</button>
                    </form>
                </div>
            `;
            
            // Add event listeners for upvote/downvote and comment form
            postDiv.querySelector('.upvote-btn').addEventListener('click', () => handleVote(post.id, 'upvote'));
            postDiv.querySelector('.downvote-btn').addEventListener('click', () => handleVote(post.id, 'downvote'));
            postDiv.querySelector('.comment-form').addEventListener('submit', handleCommentSubmit);

            // Load comments for the post
            loadComments(post, postDiv.querySelector(`#comments-${post.id}`));

            return postDiv;
        }
        
        async function handleVote(postId, type) {
            try {
                const response = await fetch(`${API_URL}/posts/${postId}/vote?user_id=${userId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ voteType: type })
                });

                if (response.ok) {
                    loadPosts(state.currentSeries);
                } else {
                    showMessage('Failed to cast vote.');
                }
            } catch (error) {
                console.error('An error occurred:', error);
                showMessage('An error occurred. Could not cast vote.');
            }
        }

        async function handleCommentDelete(postId, commentId) {
            try {
                const response = await fetch(`${API_URL}/posts/${postId}/comments/${commentId}?user_id=${userId}`, {
                    method: 'DELETE',
                });

                if (response.ok) {
                    loadPosts(state.currentSeries);
                } else {
                    showMessage('Failed to delete comment.');
                }
            } catch (error) {
                console.error('An error occurred:', error);
                showMessage('An error occurred. Could not delete comment.');
            }
        }

        async function handleCommentSubmit(event) {
            event.preventDefault();
            const form = event.target;
            const postId = form.getAttribute('data-id');
            const commentContent = form.elements['commentContent'].value;

            if (!commentContent) {
                return;
            }
            
            const newComment = {
                content: commentContent,
                authorId: userId,
            };
            
            try {
                const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newComment)
                });

                if (response.ok) {
                    form.reset();
                    loadPosts(state.currentSeries);
                } else {
                    showMessage('Failed to post comment.');
                }
            } catch (error) {
                console.error('An error occurred:', error);
                showMessage('An error occurred. Could not post comment.');
            }
        }

        function loadComments(post, container) {
            container.innerHTML = '';
            post.comments.forEach((comment) => {
                const commentElement = document.createElement('div');
                commentElement.className = 'bg-gray-700 p-3 rounded-lg text-sm flex justify-between items-center';
                
                let deleteButton = '';
                // Only show the delete button for the author or the admin
                if (comment.authorId === userId || userId === ADMIN_ID) {
                    deleteButton = `<button class="text-gray-400 hover:text-[#e50914] transition-colors duration-200 ml-2" onclick="handleCommentDelete('${post.id}', '${comment.id}')">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>`;
                }

                commentElement.innerHTML = `
                    <div>
                        <p class="text-gray-300">${comment.content}</p>
                        <p class="text-xs text-gray-500 mt-1">by ${comment.authorId}</p>
                    </div>
                    ${deleteButton}
                `;
                container.appendChild(commentElement);
            });
        }
    </script>
</head>
<body class="bg-[#161723] flex flex-col">

    <!-- Navbar -->
    <nav class="w-full bg-[#161723] p-4 shadow-lg fixed top-0 z-50">
        <div class="flex justify-between items-center px-4 max-w-7xl mx-auto">
            <a href="#" class="flex items-center space-x-2">
                <div class="w-6 h-6 bg-[#e50914] rounded-sm"></div>
                <span class="text-2xl font-bold text-white">LEET<span class="text-[#e50914]">FLIX</span></span>
            </a>
            <div id="userIdDisplay" class="text-sm text-gray-400 hidden sm:block"></div>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main id="mainContent" class="flex flex-col md:flex-row max-w-7xl w-full mx-auto p-4 mt-20 space-y-6 md:space-y-0 md:space-x-6">

        <!-- Series List Sidebar -->
        <aside class="w-full md:w-1/4 bg-[#1e1f2b] text-white rounded-xl shadow-2xl p-6 h-fit">
            <h2 class="text-xl font-bold text-white mb-4">Series</h2>
            <div id="seriesList" class="space-y-2">
                <!-- Series buttons will be dynamically added here -->
            </div>
        </aside>

        <!-- Discussion Panel -->
        <section class="w-full md:w-3/4 bg-[#1e1f2b] text-white rounded-xl shadow-2xl p-6 space-y-6">
            <header class="flex justify-between items-center mb-4">
                <h1 id="discussionTitle" class="text-3xl font-extrabold text-[#e50914]"></h1>
                <button id="addPostBtn" class="bg-[#e50914] hover:bg-[#e50914] text-white font-bold py-2 px-4 rounded-lg shadow-lg transition-colors duration-200">
                    Add Post
                </button>
            </header>
            <div id="postsContainer" class="space-y-8">
                <!-- Posts will be dynamically loaded here -->
            </div>
        </section>
    </main>
    
    <!-- Message Box -->
    <div id="messageBox" class="hidden fixed top-24 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-lg z-50 text-sm">
        Message
    </div>

    <!-- Scroll to top button -->
    <button id="scrollToTopBtn" class="fixed bottom-8 right-8 p-3 bg-gray-800 text-[#e50914] rounded-full shadow-lg transition-all duration-300 transform scale-0 z-50 hover:bg-gray-700 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
    </button>

    <!-- Post creation modal -->
    <div id="postModal" class="hidden fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center">
        <div class="bg-[#1e1f2b] p-8 rounded-xl shadow-2xl max-w-lg w-full relative">
            <button id="closeModalBtn" class="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
            <h2 class="text-2xl font-bold text-white mb-6 text-center">Create a New Post</h2>
            <form id="postForm" class="space-y-4">
                <div>
                    <label for="postTitle" class="block text-sm font-medium text-gray-300 mb-1">Title</label>
                    <input type="text" id="postTitle" name="postTitle" class="w-full p-3 rounded-lg bg-gray-700 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#e50914]" placeholder="Enter post title">
                </div>
                <div>
                    <label for="postContent" class="block text-sm font-medium text-gray-300 mb-1">Content</label>
                    <textarea id="postContent" name="postContent" rows="6" class="w-full p-3 rounded-lg bg-gray-700 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#e50914]" placeholder="Write your post content here..."></textarea>
                </div>
                <button type="submit" class="w-full bg-[#e50914] hover:bg-[#e50914] text-white font-bold py-3 px-4 rounded-lg transition-colors duration-200">
                    Post Discussion
                </button>
            </form>
        </div>
    </div>

    <script>
        // Get the button element
        const scrollToTopBtn = document.getElementById('scrollToTopBtn');

        // Show/hide the button based on scroll position
        window.onscroll = function() {
            // Check if the user has scrolled from the topmost position
            if (document.body.scrollTop > 0 || document.documentElement.scrollTop > 0) {
                scrollToTopBtn.classList.remove('scale-0');
                scrollToTopBtn.classList.add('scale-100');
            } else {
                scrollToTopBtn.classList.remove('scale-100');
                scrollToTopBtn.classList.add('scale-0');
            }
        };

        // Scroll to the top when the button is clicked
        scrollToTopBtn.onclick = function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        };
    </script>
</body>
</html>
"""

# Route to serve the HTML file.
@app.route('/')
def index():
    return HTML_CONTENT

# API endpoint to get all posts for a specific series
@app.route('/posts/<string:series_name>', methods=['GET'])
def get_posts(series_name):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    posts = []
    try:
        cursor = connection.cursor(dictionary=True)
        # Fetch posts
        sql = """
            SELECT p.id, p.series, p.title, p.content, p.author_id, p.timestamp, 
                   COUNT(CASE WHEN v.vote_type = 'upvote' THEN 1 END) AS upvote_count,
                   COUNT(CASE WHEN v.vote_type = 'downvote' THEN 1 END) AS downvote_count
            FROM posts p
            LEFT JOIN votes v ON p.id = v.post_id
            WHERE p.series = %s
            GROUP BY p.id
            ORDER BY upvote_count DESC, p.timestamp DESC;
        """
        cursor.execute(sql, (series_name,))
        post_results = cursor.fetchall()

        # For each post, fetch comments and votes
        for post in post_results:
            # Fetch comments
            comment_sql = "SELECT id, content, author_id FROM comments WHERE post_id = %s ORDER BY timestamp ASC;"
            cursor.execute(comment_sql, (post['id'],))
            comments = cursor.fetchall()
            post['comments'] = comments
            
            # Fetch vote user IDs
            vote_sql = "SELECT user_id, vote_type FROM votes WHERE post_id = %s;"
            cursor.execute(vote_sql, (post['id'],))
            vote_results = cursor.fetchall()
            
            post['upvotes'] = [v['user_id'] for v in vote_results if v['vote_type'] == 'upvote']
            post['downvotes'] = [v['user_id'] for v in vote_results if v['vote_type'] == 'downvote']
            
            posts.append(post)

        return jsonify(posts)
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API endpoint to create a new post
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    if not data or 'series' not in data or 'title' not in data or 'content' not in data or 'authorId' not in data:
        return jsonify({'error': 'Missing data'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    try:
        cursor = connection.cursor()
        new_post_id = str(uuid.uuid4())
        sql = "INSERT INTO posts (id, series, title, content, author_id, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (new_post_id, data['series'], data['title'], data['content'], data['authorId'], datetime.datetime.now())
        cursor.execute(sql, values)
        connection.commit()
        return jsonify({'message': 'Post created successfully', 'id': new_post_id}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API endpoint to delete a post
@app.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_post(post_id):
    user_id = request.args.get('user_id')
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    try:
        cursor = connection.cursor()
        sql = "SELECT author_id FROM posts WHERE id = %s"
        cursor.execute(sql, (post_id,))
        post_author = cursor.fetchone()
        
        if not post_author:
            return jsonify({'error': 'Post not found'}), 404
            
        if post_author[0] != user_id and user_id != 'admin-1234':
            return jsonify({'error': 'Unauthorized to delete this post'}), 403
            
        delete_sql = "DELETE FROM posts WHERE id = %s"
        cursor.execute(delete_sql, (post_id,))
        connection.commit()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API endpoint to handle upvoting or downvoting a post
@app.route('/posts/<string:post_id>/vote', methods=['POST'])
def vote_post(post_id):
    data = request.json
    user_id = request.args.get('user_id')
    vote_type = data.get('voteType')

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    try:
        cursor = connection.cursor()
        
        # Check if the user has already voted on this post
        check_sql = "SELECT vote_type FROM votes WHERE post_id = %s AND user_id = %s"
        cursor.execute(check_sql, (post_id, user_id))
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            if existing_vote[0] == vote_type:
                # User is unvoting, delete the vote
                delete_sql = "DELETE FROM votes WHERE post_id = %s AND user_id = %s"
                cursor.execute(delete_sql, (post_id, user_id))
            else:
                # User is changing their vote, update the existing vote
                update_sql = "UPDATE votes SET vote_type = %s WHERE post_id = %s AND user_id = %s"
                cursor.execute(update_sql, (vote_type, post_id, user_id))
        else:
            # New vote, insert into the database
            insert_sql = "INSERT INTO votes (id, post_id, user_id, vote_type) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_sql, (str(uuid.uuid4()), post_id, user_id, vote_type))
            
        connection.commit()
        return jsonify({'message': 'Vote cast successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API endpoint to add a new comment to a post
@app.route('/posts/<string:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.json
    if not data or 'content' not in data or 'authorId' not in data:
        return jsonify({'error': 'Missing data'}), 400
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    try:
        cursor = connection.cursor()
        new_comment_id = str(uuid.uuid4())
        sql = "INSERT INTO comments (id, post_id, content, author_id, timestamp) VALUES (%s, %s, %s, %s, %s)"
        values = (new_comment_id, post_id, data['content'], data['authorId'], datetime.datetime.now())
        cursor.execute(sql, values)
        connection.commit()
        return jsonify({'message': 'Comment added successfully', 'id': new_comment_id}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# API endpoint to delete a comment
@app.route('/posts/<string:post_id>/comments/<string:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    user_id = request.args.get('user_id')
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Could not connect to database.'}), 500

    try:
        cursor = connection.cursor()
        sql = "SELECT author_id FROM comments WHERE id = %s AND post_id = %s"
        cursor.execute(sql, (comment_id, post_id))
        comment_author = cursor.fetchone()
        
        if not comment_author:
            return jsonify({'error': 'Comment not found'}), 404
            
        if comment_author[0] != user_id and user_id != 'admin-1234':
            return jsonify({'error': 'Unauthorized to delete this comment'}), 403
            
        delete_sql = "DELETE FROM comments WHERE id = %s AND post_id = %s"
        cursor.execute(delete_sql, (comment_id, post_id))
        connection.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)