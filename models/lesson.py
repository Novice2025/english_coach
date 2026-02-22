from database.db import db

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(50))  # 'video' or 'pdf'
    video_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

    # This line tells Lesson how to find its parent Module
    module = db.relationship('Module', backref=db.backref('lesson_list', lazy=True))

    def __repr__(self):
        return f'<Lesson {self.title}>'
