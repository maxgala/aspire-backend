import sys
import json
import logging
from datetime import datetime, timedelta

from chat import Chat, ChatType, ChatStatus, credit_mapping, mandatory_date
from base import Session
from role_validation import UserGroups, check_auth
from cognito_helpers import get_users, admin_update_remaining_chats_frequency

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_chats(session, email=None, status=None, fixed_date=None, expiry_date=None, order_by=None, num=None):
    if email:
        query = session.query(Chat).filter(Chat.senior_executive == email)
    else:
        query = session.query(Chat)

    if status:
        query = query.filter(Chat.chat_status.in_(status))

    if fixed_date == 'DATED':
        query = query.filter(Chat.fixed_date != None)
    elif fixed_date == 'UNDATED':
        query = query.filter(Chat.fixed_date == None)

    if expiry_date == 'DATED':
        query = query.filter(Chat.expiry_date != None)
    elif expiry_date == 'UNDATED':
        query = query.filter(Chat.expiry_date == None)

    if order_by == 'fixed_date':
        query = query.order_by(Chat.fixed_date)
    elif order_by == 'expiry_date':
        query = query.order_by(Chat.expiry_date)

    if num:
        query = query.limit(num)

    chats = query.all()
    return chats

def init_periods(user, current_date):
    frequency = int(user['custom:declared_chats_freq'])
    start_date = datetime.fromtimestamp(int(user['custom:start_date']))
    end_date = datetime.fromtimestamp(int(user['custom:end_date']))

    if current_date > start_date:
        start_date = current_date

    periods = {}
    period_idx = 0

    delta = (end_date - start_date)/frequency
    curr_from = start_date
    while curr_from < end_date:
        curr_to = curr_from + delta
        periods[period_idx] = ((curr_from, curr_to))

        period_idx += 1
        curr_from = curr_to
    return periods

def populate_periods(chats, periods):
    periods_chats_freq = [0] * len(periods)
    for chat in chats:
        for idx, (start, end) in periods.items():
            if chat.chat_status != ChatStatus.CANCELED:
                if (chat.fixed_date and start <=  chat.fixed_date < end) \
                    or (chat.expiry_date and start <=  chat.expiry_date < end):
                    periods_chats_freq[idx] += 1
                    break
    return periods_chats_freq

def next_best_period(periods_chats_freq):
    weighted_periods = [0] * len(periods_chats_freq)
    min_, min_idx = sys.maxsize, -1
    for current_idx, _ in enumerate(periods_chats_freq):
        for distance_idx, num_chats in enumerate(periods_chats_freq):
            if distance_idx == current_idx:
                weighted_periods[current_idx] += 2*num_chats
            else:
                distance = abs(distance_idx - current_idx)
                weighted_periods[current_idx] += (num_chats/distance)

        if weighted_periods[current_idx] < min_:
            min_ = weighted_periods[current_idx]
            min_idx = current_idx
    return min_idx

def process_active_chats(user, chats, current_date, next_date):
    num_active_undated_unbooked = 0
    for chat in chats:
        # active dated
        if chat.chat_status == ChatStatus.ACTIVE and chat.fixed_date:
            if chat.fixed_date < current_date:
                chat.chat_status = ChatStatus.CANCELED
        # active undated
        elif chat.chat_status == ChatStatus.ACTIVE and not chat.fixed_date:
            if chat.expiry_date < current_date or chat.expiry_date > next_date:
                num_active_undated_unbooked += 1
                chat.chat_status = ChatStatus.PENDING
                admin_update_remaining_chats_frequency(user['email'], 1)
                if chat.expiry_date < current_date:
                    chat.expiry_date = None
    return num_active_undated_unbooked


def update_scheduling_periods(chats, periods, periods_frequency):
    for chat in chats:
        if chat.chat_status == ChatStatus.PENDING and not chat.expiry_date:
            schedule_period = next_best_period(periods_frequency)
            periods_frequency[schedule_period] += 1

            _, end_date = periods[schedule_period]
            chat.expiry_date = end_date

def activate_expiring_chats(user, chats, current_date, next_date):
    num_activated = 0
    for chat in chats:
        # pending undated
        if chat.chat_status == ChatStatus.PENDING and not chat.fixed_date and chat.expiry_date:
            # activate chats expiring this week
            if current_date <= chat.expiry_date <= next_date:
                num_activated += 1

                chat.chat_status = ChatStatus.ACTIVE
                admin_update_remaining_chats_frequency(user['email'], -1)
    return num_activated

# active(i.e. unbooked) chats
#   active dated chats
#       - if current_date > fixed_date => expired; set chat_status to CANCELED (notification/refunds?)
#   active undated chats
#       - if current_date  > expiry_date                 => expired; set chat_status to PENDING and refund +1 remaining_chats_frequency
#                                                           this is to be rescheduled. So, set expiry_date to None
#       - if current_date <= expiry_date  <= next_date    => expiring this scheduling window; NOOP
#                                                           NOOP, leave it active
#       - if                 expiry_date > next_date    => not expiring; set chat_status to PENDING and refund +1 remaining_chats_frequency
#                                                           no need to reschedule
#
# pending chats
#   pending dated chats => N/A; a new Chat with fixed_date is automatically activated
#   pending undated
#       pending undated expiry_date specified      => NOOP
#       pending undated expiry_date NOT specified  => find a period to be scheduled in
def schedule_user(session, user, current_date, next_date):
    chats = get_chats(session, email=user['email'], status=['PENDING', 'ACTIVE'])
    # check active chats
    num_active_undated_unbooked = process_active_chats(user, chats, current_date, next_date)

    # initialize and populate periods
    # chats to be taken into account
    #   - active chats
    #   - pending (undated) chats with expiry_date specified
    periods = init_periods(user, current_date)
    periods_frequency = populate_periods(chats, periods)

    # chats to be (re)scheduled
    #   - pending (undated) chats with expiry_date NOT specified
    update_scheduling_periods(chats, periods, periods_frequency)

    num_pending_undated_activated = activate_expiring_chats(user, chats, current_date, next_date)
    logger.info("User {}: Unbooked={}, Activated={}".format(user['email'], num_active_undated_unbooked, num_pending_undated_activated))
    return (num_active_undated_unbooked - num_pending_undated_activated)

def schedule_activate(session, default_num_activate, num_carry_over):
    num_activate = default_num_activate + num_carry_over
    if num_activate <= 0:
        return

    chats = get_chats(session, status=['PENDING'], expiry_date='DATED', order_by='expiry_date', num=num_activate)
    for chat in chats:
        chat.chat_status = ChatStatus.ACTIVE
        user = get_users(filter_=('email', chat.senior_executive))
        admin_update_remaining_chats_frequency(user['attributes']['email'], -1)

def handler(event, context):
    # check authorization
    authorized_groups = [
        UserGroups.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_groups)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    try:
        session = Session()
        default_num_activate = int(event["queryStringParameters"]["num_activate"])
        current_date = datetime.strptime(event["queryStringParameters"]["current_date"], "%d/%m/%Y")
        next_date = current_date + timedelta(weeks=1)
        logger.info("num_activate={}, current_date={}, next_date={}"\
            .format(default_num_activate, current_date.strftime("%d/%m/%Y"), next_date.strftime("%d/%m/%Y")))

        users = get_users(user_type='MENTOR')
        num_carry_over = 0
        for user in users:
            num_carry_over += schedule_user(session, user['attributes'], current_date, next_date)

        logger.info("Carry Forward={}".format(num_carry_over))
        schedule_activate(session, default_num_activate, num_carry_over)
    except Exception as e:
        session.rollback()
        session.close()
        import traceback; traceback.print_exc()
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "exception caught while running scheduler {}".format(e)
            })
        }

    session.commit()
    session.close()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "next_date":next_date.strftime("%d/%m/%Y")
        })
    }
