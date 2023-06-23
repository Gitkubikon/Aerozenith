from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime
import json
import os
import shutil

app = Flask(__name__)

CORS(app)
# CORS(app, resources={r"/*": {"origins": "http://localhost:80"}})
# CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": "*"}})
app.config['SECRET_KEY'] = 'sabalimbalim'  # Set a secret key for JWT
jwt = JWTManager(app)  # Initialize JWT
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

CONTENT_FOLDER = "content"
METADATA_FILE = "metadata.json"

# Generate JWT token
@app.route('/login', methods=['POST'])
def login():
    with open('config.json', 'r') as f:
        config = json.load(f)
    if request.json is not None:
        password = request.json.get('password', '')
        username = request.json.get('username', '')
    else:
        password = ''
        username = ''
    if username in config['users'] and password == config['users'][username]:
        token = create_access_token(identity=username)
        return jsonify(success=True, token=token)
    else:
        return jsonify(success=False, error='Invalid credentials'), 401

# Protected routes
@app.route('/metadata', methods=['GET'])
def get_content_metadata():
    try:
        with open(os.path.join(CONTENT_FOLDER, 'metadata.json')) as f:
            return f.read()
    except FileNotFoundError:
        return 'Metadata not found', 404

@app.route('/articles/<category>/<article>', methods=['GET'])
def get_article(category, article):
    article_folder = os.path.join(CONTENT_FOLDER, category, article)
    if not os.path.exists(article_folder):
        return jsonify({"message": "Article not found"}), 404

    with open(os.path.join(article_folder, "index.md"), "r") as f:
        content = f.read()

    metadata = load_metadata()
    if article not in metadata[category]:
        return jsonify({"message": "Metadata not found for article"}), 404

    save_metadata(metadata)

    return jsonify({"content": content, "metadata": metadata[category][article]}), 200


@app.route('/reindex', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)  # Making the JWT optional for the OPTIONS preflight
def reindex_articles():
    metadata = load_metadata()

    # Load the metadata template
    with open(os.path.join(CONTENT_FOLDER, "mt.json"), "r") as f:
        template = json.load(f)

    # Iterate through all directories inside the CONTENT_FOLDER
    for root, dirs, files in os.walk(CONTENT_FOLDER):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            index_file = os.path.join(dir_path, "index.md")

            # Check if the directory has an index.md file
            if os.path.isfile(index_file):
                # Get the relative path of the directory
                path = os.path.relpath(dir_path, CONTENT_FOLDER)
                category, article = os.path.split(path)

                # Ensure category and article are present in metadata
                if category not in metadata:
                    metadata[category] = {}

                if article not in metadata[category]:
                    metadata[category][article] = template.copy()
                    metadata[category][article]["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Update the modified_at timestamp
                metadata[category][article]["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Process images
                image_dir = os.path.join(dir_path, "images")
                if os.path.exists(image_dir):
                    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
                    image_paths = [os.path.relpath(os.path.join(image_dir, f), CONTENT_FOLDER) for f in image_files]
                    metadata[category][article]["images"] = image_paths
                else:
                    metadata[category][article]["images"] = []

                # Process cover image
                cover_dir = os.path.join(dir_path, "cover")
                if os.path.exists(cover_dir):
                    cover_files = [f for f in os.listdir(cover_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                    if cover_files:
                        cover_path = os.path.relpath(os.path.join(cover_dir, cover_files[0]), CONTENT_FOLDER)
                        metadata[category][article]["cover"] = cover_path
                else:
                    metadata[category][article]["cover"] = ""

                # Process background image
                background_dir = os.path.join(dir_path, "background")
                if os.path.exists(background_dir):
                    background_files = [f for f in os.listdir(background_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                    if background_files:
                        background_path = os.path.relpath(os.path.join(background_dir, background_files[0]), CONTENT_FOLDER)
                        metadata[category][article]["background"] = background_path
                else:
                    metadata[category][article]["background"] = ""

                # Process videos
                video_dir = os.path.join(dir_path, "videos")
                if os.path.exists(video_dir):
                    video_files = [f for f in os.listdir(video_dir) if f.lower().endswith((".mp4", ".avi", ".mov", ".wmv"))]
                    video_paths = [os.path.relpath(os.path.join(video_dir, f), CONTENT_FOLDER) for f in video_files]
                    metadata[category][article]["videos"] = video_paths
                else:
                    metadata[category][article]["videos"] = []

    # Remove metadata entries for files that do not exist on the disk
    for category, articles in metadata.items():
        for article, article_data in articles.items():
            # Check images
            if "images" in article_data:
                image_paths = article_data["images"]
                for image_path in image_paths.copy():
                    if not os.path.exists(os.path.join(CONTENT_FOLDER, image_path)):
                        image_paths.remove(image_path)

            # Check cover image
            cover_image = article_data.get("cover", "")
            if cover_image and not os.path.exists(os.path.join(CONTENT_FOLDER, cover_image)):
                article_data["cover"] = ""

            # Check background image
            background_image = article_data.get("background", "")
            if background_image and not os.path.exists(os.path.join(CONTENT_FOLDER, background_image)):
                article_data["background"] = ""

            # Check videos
            if "videos" in article_data:
                video_paths = article_data["videos"]
                for video_path in video_paths.copy():
                    if not os.path.exists(os.path.join(CONTENT_FOLDER, video_path)):
                        video_paths.remove(video_path)

    # Save updated metadata
    save_metadata(metadata)
    return jsonify({"message": "Articles reindexed successfully"}), 200



@app.route('/articles/<category>/<article>', methods=['PATCH'])
@jwt_required()
def patch_article(category, article):
    article_folder = os.path.join(CONTENT_FOLDER, category, article)
    if not os.path.exists(article_folder):
        return jsonify({"message": "Article not found"}), 404

    if request.json is not None:
        content = request.json.get('content', '')
        print(content)
        with open(os.path.join(article_folder, "index.md"), "w") as f:
            f.write(content)

    metadata = load_metadata()
    if article not in metadata[category]:
        return jsonify({"message": "Metadata not found for article"}), 404

    # req_data = request.get_json()
    # metadata[category][article].update(req_data)
    metadata[category][article]["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_metadata(metadata)

    return jsonify({"metadata": metadata[category][article]}), 200


@app.route('/articles/<category>/<article>', methods=['PUT'])
@jwt_required()
def put_article(category, article):
    article_folder = os.path.join(CONTENT_FOLDER, category, article)
    if os.path.isdir(article_folder):
        return jsonify({"message": "Article already exists"}), 409

    os.makedirs(article_folder, exist_ok=True)

    with open(os.path.join(article_folder, "index.md"), "w") as f:
        f.write("")

    content_type = request.content_type
    if content_type == 'application/json':
        payload = request.get_json()
    else:
        payload = None

    template = None
    with open(os.path.join(CONTENT_FOLDER, "mt.json"), "r") as f:
        template = json.load(f)

    metadata = load_metadata()
    if category not in metadata:
        metadata[category] = {}
    if article not in metadata[category]:
        metadata[category][article] = template.copy()

    if payload:
        metadata[category][article].update(payload)

    for key in template:
        if key not in metadata[category][article]:
            metadata[category][article][key] = template[key]

    metadata[category][article]["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_metadata(metadata)

    return jsonify({"metadata": metadata[category][article]}), 201





@app.route("/media/<category>/<article>/<media_type>/<filename>", methods=["PUT"])
@jwt_required()
def put_media(category, article, media_type, filename):
    if media_type not in ["images", "videos", "background", "cover"]:
        return f"{media_type} not allowed", 400

    media_dir = os.path.join(CONTENT_FOLDER, category, article, media_type)

    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    file_path = os.path.join(media_dir, filename)

    # Load current metadata
    metadata = load_metadata()

    # If a cover or background exists, remove it
    if media_type in ["cover", "background"]:
        if metadata[category][article].get(media_type):
            old_file_path = os.path.join(CONTENT_FOLDER, metadata[category][article][media_type])
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        metadata[category][article][media_type] = category + "/" + article + "/" + media_type + "/" + filename
    elif media_type in ["images", "videos"]:
        if os.path.exists(file_path):
            os.remove(file_path)
        metadata[category][article][media_type].append(category + "/" + article + "/" + media_type + "/" + filename)

    # Save the uploaded file
    uploaded_file = request.files['file']
    uploaded_file.save(file_path)

    # Update metadata for the uploaded image
    metadata[category][article]["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_metadata(metadata)

    return jsonify({"message": "Media uploaded successfully"}), 201




@app.route("/media/<category>/<article>/<media_type>/<filename>", methods=["GET"])
def get_media(category, article, media_type, filename):
    if media_type not in ["images", "videos", "background", "cover"]:
        return f"{media_type} not allowed", 400

    media_dir = os.path.join(CONTENT_FOLDER, category, article, media_type)

    if not os.path.exists(media_dir):
        return f"Media not found for {category}/{article}/{media_type}/{filename}", 404

    file_path = os.path.join(media_dir, filename)

    if not os.path.exists(file_path):
        return f"Media not found for {category}/{article}/{media_type}/{filename}", 404

    return send_from_directory(media_dir, filename), 200


@app.route('/media/<category>/<article>/<media_type>/<media>', methods=['DELETE'])
@jwt_required()
def delete_media(category, article, media_type, media):
    # Check if article and media exist

    if media_type == "cover":
        media_path = os.path.join(CONTENT_FOLDER, category, article, f"{media}")
    else:
        media_path = os.path.join(CONTENT_FOLDER, category, article, media_type, f"{media}")

    if not os.path.exists(media_path):
        return f"{media_type} with id {media} not found for article {article} in category {category}", 404

    # Delete the media file
    os.remove(media_path)

    # Update metadata for the deleted media
    metadata = load_metadata()
    if media_type not in metadata[category][article]:
        metadata[category][article][media_type] = {}
    metadata[category][article][media_type].remove(category + "/" + article + "/" + media_type + "/" + media)
    metadata[category][article]["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_metadata(metadata)

    return f"{media_type} with id {media} deleted for article {article} in category {category}", 200


@app.route('/articles/<category>/<article>', methods=['DELETE'])
@jwt_required()
def delete_article(category, article):
    article_folder = os.path.join(CONTENT_FOLDER, category, article)
    if not os.path.exists(article_folder):
        return jsonify({"message": "Article not found"}), 404

    metadata = load_metadata()
    if article not in metadata[category]:
        return jsonify({"message": "Metadata not found for article"}), 404

    # Use shutil.rmtree for deleting directories
    shutil.rmtree(article_folder)
    del metadata[category][article]
    save_metadata(metadata)

    return jsonify({"message": "Article deleted"}), 200


def load_metadata():
    metadata = {}
    try:
        with open(os.path.join(CONTENT_FOLDER, METADATA_FILE), "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"Metadata file {METADATA_FILE} not found")
    except json.JSONDecodeError as e:
        print(f"Error loading metadata file: {e}")
    return metadata


def save_metadata(metadata):
    with open(os.path.join(CONTENT_FOLDER, METADATA_FILE), "w") as f:
        json.dump(metadata, f, indent=4)  # adding indent for better readability of the output file


if __name__ == '__main__':
    dev_mode = False
    if dev_mode:
        app.run(debug=True, port=3000)
    else:
        app.run(host='0.0.0.0', port=80)
