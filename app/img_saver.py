import hashlib, os, uuid
from werkzeug.utils import secure_filename
from models import Cover
from app import db, app

class ImgSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Cover(
            id=str(uuid.uuid4()),
            file_name=file_name,
            MIME_type=self.file.mimetype,
            MD5_hash=self.MD5_hash)
        self.file.save(
            os.path.join(app.config['UPLOAD_FOLDER'],
                         self.img.storage_filename))
        db.session.add(self.img)
        db.session.commit()
        return self.img

    def __find_by_md5_hash(self):
        self.MD5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Cover).filter(Cover.MD5_hash == self.MD5_hash)).scalar()