from models.models import User
from models.models import File
from services.database import db
from flask import Blueprint, render_template
from flask import request, redirect, session, url_for, jsonify, send_from_directory
import services.identity as idt
import os
import uuid

files_router = Blueprint('files', __name__, template_folder="../template/")

@files_router.route("/get_files")
def get_files():
    user = idt.get_user_info(session["token"])
    if not user:
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(userName=user["preferred_username"]).first()
    
    files = File.query.filter_by(user_id=user.id).all()

    return jsonify([file.serialize() for file in files])

@files_router.route("/upload", methods=["POST"])
def upload():
    user = idt.get_user_info(session["token"])
    if not user:
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(userName=user["preferred_username"]).first()
    
    file = request.files["file"]
    file_extension = os.path.splitext(file.filename)[1]
    path = f"uploads/{uuid.uuid4()}{file_extension}"
    file.save(path)
    
    new_file = File(
        user_id=user.id,
        name=file.filename,
        size=file.content_length,
        type=file.content_type,
        path=path
    )
    
    db.session.add(new_file)
    db.session.commit()
    
    return "File uploaded successfully", 201

@files_router.route("/delete/<file_id>", methods=["DELETE"])
def delete(file_id):
    user = idt.get_user_info(session["token"])
    if not user:
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(userName=user["preferred_username"]).first()
    
    file = File.query.filter_by(id=file_id).first()
    if not file:
        return "File not found", 404
    if file.user_id != user.id:
        return "Unauthorized", 401
    
    os.remove(file.path)

    db.session.delete(file)
    db.session.commit()
    
    return jsonify(message="File deleted successfully"), 200

@files_router.route("/download/<file_id>")
def download(file_id):
    user = idt.get_user_info(session["token"])
    if not user:
        return redirect(url_for("auth.login"))
    
    user = User.query.filter_by(userName=user["preferred_username"]).first()
    
    file = File.query.filter_by(id=file_id).first()
    if not file:
        return "File not found", 404
    if file.user_id != user.id:
        return "Unauthorized", 401
    
    upload_folder = os.path.abspath("uploads")
    file_path = os.path.abspath(file.path)

    print("files", upload_folder, file_path)

    if not file_path.startswith(upload_folder):
        return "Invalid file path", 400

    filename = os.path.basename(file_path)

    # Serve the file from the uploads directory with the correct content type
    return send_from_directory(upload_folder, filename, as_attachment=True, attachment_filename=file.name)