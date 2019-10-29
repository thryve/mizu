from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
import arrow
from sqlalchemy.ext.mutable import MutableDict, MutableList
import enum
import sys
import bcrypt
import random
import os

app = Flask(__name__)

PRODUCTION_DB = os.environ['PRODUCTION_DB']
LOCAL_DB = os.environ['LOCAL_DB']
GENERIC_PASSWORD = os.environ['GENERIC_PASSWORD']

SQLALCHEMY_BINDS = {
    'local' : LOCAL_DB
}

app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION_DB
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
utcnow_datetime_aware = arrow.utcnow().datetime

class Statuses(enum.Enum):
        # Normal statuses.
        CREATED = 0
        SHIPPED = 1
        REGISTERED = 2
        PROCESSING = 3
        ANALYZING = 4
        COMPLETE = 5

        # Abnormal statuses.
        LOST = -1

'''
For access to production database
'''
db = SQLAlchemy(app)
class ProductionUser(db.Model):
    __tablename__ = "users"

    VISIBLE = ("any_one", "registered_only", "only_me")

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(45))
    password = db.Column(db.LargeBinary(60), nullable=False)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=True)
    visible_to = db.Column(
        postgresql.ENUM(*VISIBLE, name="visible_enum"),
        nullable=False, default=VISIBLE[0]
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False, default=arrow.utcnow().datetime
    )
    last_login_at = db.Column(db.DateTime(timezone=True))
    last_access_at = db.Column(db.DateTime(timezone=True))
    has_finished_onboarding = db.Column(db.Boolean, default=False)
    has_completed_survey = db.Column(db.Boolean, nullable=False, default=False)
    has_received_pmf_survey = db.Column(db.Boolean, nullable=False, default=False)
    has_completed_pmf_survey = db.Column(db.Boolean, nullable=False, default=False)
    is_signed_up = db.Column(db.Boolean, nullable=False, default=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime(timezone=True))
    recharge_hash = db.Column(db.Text(), unique=True)
    shopify_id = db.Column(db.Text(), unique=True)
    # samples = db.relationship("Sample", backref="users", lazy="dynamic")
    diet = db.Column(MutableDict.as_mutable(postgresql.JSONB))
    lifestyle = db.Column(MutableDict.as_mutable(postgresql.JSONB))
class ProductionSample(db.Model):
    # __bind_key__ = 'local'
    __tablename__ = "samples"
    # user = db.relationship("User", lazy="subquery")


    id = db.Column(db.String(5), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(
        postgresql.ENUM(Statuses),
        default=Statuses(0),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        nullable=False
    )
    registered_at = db.Column(db.DateTime(timezone=True))
    sampled_at = db.Column(db.Date())
    last_updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        onupdate=utcnow_datetime_aware,
        nullable=False
    )
    is_ubiome_data = db.Column(db.Boolean, default=False, nullable=False)
    data_uri = db.Column(db.String(256))
    # metrics = db.relationship(
    #     "SampleMetrics",
    #     uselist=False, backref=db.backref("sample", uselist=False)
    # )
    notes = db.Column(db.Text())

    def __repr__(self):
        return f"<[Production]Sample id={id}>"
class ProductionSampleMetrics(db.Model):
    __tablename__ = "sample_metrics"

    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(
        db.String(5), db.ForeignKey("samples.id"),
        nullable=False, unique=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        nullable=False
    )
    last_updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware, onupdate=utcnow_datetime_aware,
        nullable=False
    )

    wellness_score = db.Column(db.Float, nullable=False)
    diversity_index = db.Column(db.Float, nullable=False)
    evenness = db.Column(db.Float, nullable=False)
    richness = db.Column(db.Integer, nullable=False)
    total_species_count = db.Column(db.Integer, nullable=False)
    ecosystem = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    growth = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    probiotics = db.Column(
        MutableList.as_mutable(postgresql.JSONB),
        nullable=False
    )
    recommendations = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    symptoms = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )

    def __repr__(self):
        return f"<[Production]SampleMetrics id:{self.id!r} sample_id={self.sample_id!r}>"

'''
For access to local database.
Created two different SQLAlchemy objects to prevent sharing of metadata.
For more info:
# https://stackoverflow.com/questions/15336778/using-same-name-of-tables-with-different-binds-in-flask?noredirect=1&lq=1
'''
db2 = SQLAlchemy(app)
class LocalUser(db2.Model):
    __bind_key__ = 'local'
    __tablename__ = 'users'

    VISIBLE = ("any_one", "registered_only", "only_me")

    id = db2.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db2.Column(db.String(45))
    password = db.Column(db.LargeBinary(60), nullable=False)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=True)
    visible_to = db.Column(
        postgresql.ENUM(*VISIBLE, name="visible_enum"),
        nullable=False, default=VISIBLE[0]
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False, default=arrow.utcnow().datetime
    )
    last_login_at = db.Column(db.DateTime(timezone=True))
    last_access_at = db.Column(db.DateTime(timezone=True))
    has_finished_onboarding = db.Column(db.Boolean, default=False)
    has_completed_survey = db.Column(db.Boolean, nullable=False, default=False)
    has_received_pmf_survey = db.Column(db.Boolean, nullable=False, default=False)
    has_completed_pmf_survey = db.Column(db.Boolean, nullable=False, default=False)
    is_signed_up = db.Column(db.Boolean, nullable=False, default=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime(timezone=True))
    recharge_hash = db.Column(db.Text(), unique=True)
    shopify_id = db.Column(db.Text(), unique=True)
    # samples = db.relationship("Sample", backref="users", lazy="dynamic")
    diet = db.Column(MutableDict.as_mutable(postgresql.JSONB))
    lifestyle = db.Column(MutableDict.as_mutable(postgresql.JSONB))
class LocalSample(db2.Model):
    __bind_key__ = 'local'
    __tablename__ = 'samples'
    # user = db.relationship("User", lazy="subquery")


    id = db.Column(db.String(5), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(
        postgresql.ENUM(Statuses),
        default=Statuses(0),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        nullable=False
    )
    registered_at = db.Column(db.DateTime(timezone=True))
    sampled_at = db.Column(db.Date())
    last_updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        onupdate=utcnow_datetime_aware,
        nullable=False
    )
    is_ubiome_data = db.Column(db.Boolean, default=False, nullable=False)
    data_uri = db.Column(db.String(256))
    # metrics = db.relationship(
    #     "SampleMetrics",
    #     uselist=False, backref=db.backref("sample", uselist=False)
    # )
    notes = db.Column(db.Text())
class LocalSampleMetrics(db2.Model):
    __bind_key__ = 'local'
    __tablename__ = "sample_metrics"

    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(
        db.String(5), db.ForeignKey("samples.id"),
        nullable=False, unique=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware,
        nullable=False
    )
    last_updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow_datetime_aware, onupdate=utcnow_datetime_aware,
        nullable=False
    )

    wellness_score = db.Column(db.Float, nullable=False)
    diversity_index = db.Column(db.Float, nullable=False)
    evenness = db.Column(db.Float, nullable=False)
    richness = db.Column(db.Integer, nullable=False)
    total_species_count = db.Column(db.Integer, nullable=False)
    ecosystem = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    growth = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    probiotics = db.Column(
        MutableList.as_mutable(postgresql.JSONB),
        nullable=False
    )
    recommendations = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )
    symptoms = db.Column(
        MutableDict.as_mutable(postgresql.JSONB),
        nullable=False
    )

    def __repr__(self):
        return f"<[LOCAL]SampleMetrics id:{self.id!r} sample_id={self.sample_id!r}>"

def hash_password(password):
    if isinstance(password, str):
        password = password.encode()

    password = bcrypt.hashpw(
        password,
        bcrypt.gensalt(rounds=12)
    )
    return password

if __name__ == "__main__":
    param_name = str(sys.argv[1])
    db_user = []
    if param_name == "--email":
        email = str(sys.argv[2])
        db_user = ProductionUser.query.filter_by(email=email).all()

    if param_name == "--id":
        id = int(sys.argv[2])
        user = ProductionUser.query.get(id)
        if user is not None:
            db_user.append(user)

    if len(db_user) == 0:
        print(f"[-] {email if email else id} doesn't exist in database.")
    else:
        user = db_user[0]
        random_user_id = random.randrange(500,10000,1)
        new_user = LocalUser(
            id = random_user_id,
            username = f"user{random_user_id}",
            email = user.email,
            password = hash_password(GENERIC_PASSWORD),
            first_name = user.first_name,
            last_name = user.last_name,
            visible_to='any_one')

        print(f"[+] Adding {user.email} to users with id: {random_user_id}")
        db.session.add(new_user)
        db.session.commit()

        db_samples = ProductionSample.query.filter_by(user_id=user.id).all()
        sample = None
        if len(db_samples) > 0:
            for sample in db_samples:

                new_sample = LocalSample(
                    id=sample.id,
                    user_id=random_user_id,
                    status=sample.status,
                    registered_at=sample.registered_at,
                    last_updated_at=sample.last_updated_at,
                    data_uri=sample.data_uri
                )
                print(f"[+] Adding {sample.id} to samples.")
                db.session.add(new_sample)
                db.session.commit()

                db_sample_metrics = ProductionSampleMetrics.query.filter_by(sample_id=sample.id).all()
                if db_sample_metrics:
                    # absurdley high sample_metrics id to ensure that there's no colission
                    random_sample_metric_id = random.randrange(10000, 100000,1)
                    sample_metrics = db_sample_metrics[0]
                    new_sample_metrics = LocalSampleMetrics(
                            id=random_sample_metric_id,
                            sample_id=sample.id,
                            created_at=sample_metrics.created_at,
                            last_updated_at=sample_metrics.last_updated_at,
                            wellness_score=sample_metrics.wellness_score,
                            diversity_index=sample_metrics.diversity_index,
                            evenness=sample_metrics.evenness,
                            richness=sample_metrics.richness,
                            total_species_count=sample_metrics.total_species_count,
                            ecosystem=sample_metrics.ecosystem,
                            growth=sample_metrics.growth,
                            probiotics=sample_metrics.probiotics,
                            recommendations=sample_metrics.recommendations,
                            symptoms=sample_metrics.symptoms
                    )
                    print(f"[+] Adding {sample.id} to sample_metrics with id: {random_sample_metric_id}")
                    db.session.add(new_sample_metrics)
                    db.session.commit()
                else:
                    print(f"[-] {sample.id} doesn't have any sample_metrics")

        else:
            print(f"[-] {user.email} doesn't have any samples.")





