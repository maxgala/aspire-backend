import sys
import json
import logging
from datetime import datetime, timedelta

from chat import Chat, ChatType, ChatStatus, credit_mapping, mandatory_date
from base import Session
from role_validation import UserType, check_auth
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
        if chat.chat_status != ChatStatus.EXPIRED:
            for idx, (start, end) in periods.items():
                if (chat.fixed_date and start <= chat.fixed_date < end) \
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

def process_dated_chats(user, chats, current_date, next_date):
    for chat in chats:
        # expired
        # TODO: delta function to expire dated chats, instead of day of
        if chat.fixed_date and chat.fixed_date < current_date:
            if chat.chat_status == ChatStatus.RESERVED_PARTIAL \
               or chat.chat_status == ChatStatus.RESERVED:
                # TODO: send email notification to SE/AP(s)
                chat.chat_status = ChatStatus.RESERVED_CONFIRMED
            elif chat.chat_status == ChatStatus.ACTIVE:
                # TODO: send email notification to SE
                chat.chat_status = ChatStatus.EXPIRED

def process_undated_chats(user, chats, current_date, next_date):
    num_unbooked = 0
    for chat in chats:
        if not chat.fixed_date:
            if chat.chat_status == ChatStatus.RESERVED_PARTIAL \
               or chat.chat_status == ChatStatus.RESERVED:
                # TODO: send email notification to SE/AP(s)
                chat.chat_status = ChatStatus.RESERVED_CONFIRMED
            elif chat.chat_status == ChatStatus.ACTIVE:
                if chat.expiry_date < current_date or chat.expiry_date > next_date:
                    num_unbooked += 1
                    chat.chat_status = ChatStatus.PENDING
                    admin_update_remaining_chats_frequency(user['email'], 1)
                    if chat.expiry_date < current_date:
                        chat.expiry_date = None
    return num_unbooked

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
        if chat.chat_status == ChatStatus.PENDING and not chat.fixed_date and chat.expiry_date:
            if current_date <= chat.expiry_date < next_date:
                num_activated += 1

                chat.chat_status = ChatStatus.ACTIVE
                admin_update_remaining_chats_frequency(user['email'], -1)
    return num_activated

'''
* RESERVED_CONFIRMED        => NOOP; take into account in populating periods
* DONE                      => NOOP; take into account in populating periods

dated chats
    * PENDING               => N/A; a new Chat with fixed_date is automatically activated
    * ACTIVE                => if expired, move to EXPIRED (notification/refunds?)
    * RESERVED_PARTIAL      => if expired, move to RESERVED_CONFIRMED
    * RESERVED              => if expired, move to RESERVED_CONFIRMED

undated chats
    * PENDING               => if it doesn't have expiry_date, find a scheduling period
    * ACTIVE
        - if current_date  > expiry_date                => expired; move to PENDING, refund remaining_chats_frequency, reschedule(set expiry_date=None)
        - if current_date <= expiry_date <= next_date   => expiring this scheduling window; NOOP
        - if                 expiry_date > next_date    => not expiring; move to PENDING, refund remaining_chats_frequency
    * RESERVED_PARTIAL      => move to RESERVED_CONFIRMED
    * RESERVED              => move to RESERVED_CONFIRMED
'''
def schedule_user(session, user, current_date, next_date):
    status_list = ['PENDING', 'ACTIVE', 'RESERVED_PARTIAL', 'RESERVED', 'RESERVED_CONFIRMED', 'DONE']
    chats = get_chats(session, email=user['email'], status=status_list)
    # dated chats
    process_dated_chats(user, chats, current_date, next_date)
    # undated chats
    num_unbooked = process_undated_chats(user, chats, current_date, next_date)

    '''
    initialize and populate periods, take into account:
        * undated chats     =>          ACTIVE, RESERVED_PARTIAL, RESERVED, RESERVED_CONFIRMED and DONE chats
        * dated chats       => PENDING, ACTIVE,                             RESERVED_CONFIRMED and DONE chats with expiry_date specified
    So, take all but EXPIRED chats into account since at this stage:
        * undated chats: all are in desired states in addition to potential EXPIRED ones
        * dated chats: all are in desired states
    '''
    periods = init_periods(user, current_date)
    periods_frequency = populate_periods(chats, periods)

    '''
    chats to be (re)scheduled
        * undated chats: all with expiry_date NOT specified
    '''
    update_scheduling_periods(chats, periods, periods_frequency)

    # activate pending undated chats expiring this week
    num_expiring_activated = activate_expiring_chats(user, chats, current_date, next_date)
    logger.info("User {}: Unbooked={}, Activated={}".format(user['email'], num_unbooked, num_expiring_activated))
    return (num_unbooked - num_expiring_activated)

def schedule_activate(session, default_num_activate, num_carry_over):
    num_activate = default_num_activate + num_carry_over
    if num_activate <= 0:
        return

    chats = get_chats(session, status=['PENDING'], expiry_date='DATED', order_by='expiry_date', num=num_activate)
    for chat in chats:
        chat.chat_status = ChatStatus.ACTIVE
        user, _ = get_users(filter_=('email', chat.senior_executive))
        admin_update_remaining_chats_frequency(user['attributes']['email'], -1)

def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
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

        users, _ = get_users(user_type='MENTOR')
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
