import sys
import json
import logging

from datetime import datetime

# FOR REFERENCE
from user import User, UserType, MembershipType, IndustryTags, EducationLevel
from chat import Chat, ChatType, ChatStatus
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    #  generate database schema
    Base.metadata.create_all(engine)

    # FOR REFERENCE
    # # create a new session
    # session = Session()

    # # create users
    # superman = User(username="superman", email_address="superman@krypton.ca", first_name="Kal",
    #                 last_name="El", position="Superhero", user_type=UserType.ASPIRING_PROFESSIONAL,
    #                 birth_year="1938", education_level=EducationLevel.HIGHSCHOOL,
    #                 country="Canada", province="Quebec", credits=1000,
    #                 membership_type=MembershipType.PREMIUM, password="12345678")
    # batman = User(username="batman", email_address="batman@cave.ca", first_name="Bruce",
    #                 last_name="Wayne", position="Superhero", user_type=UserType.SENIOR_EXECUTIVE,
    #                 birth_year="1963", education_level=EducationLevel.DOCTORATE,
    #                 country="Canada", province="Ontario", credits=25,
    #                 membership_type=MembershipType.FREE_TIER, password="87654321")
    # saleh = User(username="salehman", email_address="salehman@krypton.ca", first_name="Saleh",
    #                 last_name="Bakhit", position="Superhero", user_type=UserType.ADMIN,
    #                 birth_year="1995", education_level=EducationLevel.BACHELORS,
    #                 country="Canada", province="Quebec", credits=0,
    #                 membership_type=MembershipType.PREMIUM, password="#$$&^%@#")

    # # create chats
    # chat1 = Chat(date=datetime.now(), chat_type=ChatType.ONE_ON_ONE,
    #              credits=1, chat_status=ChatStatus.PENDING)

    # # add users to chats
    # chat1.senior_executives = [batman]
    # chat1.aspiring_professionals = [superman]

    # # persists data
    # session.add(superman)
    # session.add(batman)
    # session.add(saleh)

    # session.add(chat1)

    # # commit and close session
    # session.commit()
    # session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Created Tables"
        }),
    }
