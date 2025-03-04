from flask import Blueprint, request, jsonify
from services.fidelity import buy, sell, complete_2fa_and_trade
from services.chase import buy as chase_buy, sell as chase_sell
from services.schwab import buy as schwab_buy, sell as schwab_sell
from services.firstrade import buy as firstrade_buy, sell as firstrade_sell
from services.webull import buy as webull_buy
from services.wellsfargo import buy as wells_buy, sell as wells_sell
from services.public import buy as public_buy, sell as public_sell
from services.robinhood import buy as robinhood_buy, sell as robinhood_sell
from services.fennel import buy as fennel_buy, sell as fennel_sell, complete_2fa_and_trade as fennel_complete_2fa_and_trade
import logging

import os

trade_bp = Blueprint('trade_bp', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map brokers to their respective buy and sell functions
BROKER_SERVICES = {
    'chase': {'buy': chase_buy, 'sell': chase_sell},
    'fidelity': {'buy': buy, 'sell': sell},
    'firstrade': {'buy': firstrade_buy, 'sell': firstrade_sell},
    'public': {'buy': public_buy, 'sell': public_sell},
    'schwab': {'buy': schwab_buy, 'sell': schwab_sell},
    'webull': {'buy': webull_buy},
    'wells': {'buy': wells_buy, 'sell': wells_sell},
    'robinhood': {'buy': robinhood_buy, 'sell': robinhood_sell},
    'fennel': {'buy': fennel_buy, 'sell': fennel_sell},
}

@trade_bp.route('/buy', methods=['POST'])
def buy_stock():
    try:
        data = request.json
        logger.info(f"Received buy request: {data}")
        tickers = data.get('tickers')
        broker = data.get('broker')
        quantity = data.get('quantity')
        username = data.get('username')
        password = data.get('password')

        # broker = broker.lower()
        # if broker not in BROKER_SERVICES:
        #     logger.warning(f"Unsupported broker: {broker}")
        #     return jsonify({'error': f"Unsupported broker: {broker}"}), 400

        service = BROKER_SERVICES[broker]['buy']
        response = service(
            tickers=tickers,
            dir=None,   # Adjust if you have directory profiles
            prof=None,  # Adjust if you have profiles
            trade_share_count=quantity,
            username=username,
            password=password
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing buy request: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the buy request.'}), 500

@trade_bp.route('/sell', methods=['POST'])
def sell_stock():
    try:
        data = request.json
        logger.info(f"Received sell request: {data}")
        tickers = data.get('tickers')
        broker = data.get('broker')
        quantity = data.get('quantity')
        username = data.get('username')
        password = data.get('password')

        service = BROKER_SERVICES[broker]['sell']
        response = service(
            tickers=tickers,
            dir=None,
            prof=None,
            trade_share_count=quantity,
            username=username,
            password=password
        )

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing sell request: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the sell request.'}), 500

@trade_bp.route('/complete_2fa', methods=['POST'])
def complete_2fa_endpoint():
    try:
        data = request.json
        logger.info(f"Received 2FA completion request: {data}")
        session_id = data.get('session_id')
        two_fa_code = data.get('two_fa_code')  # Required for text-based 2FA

        if not session_id:
            logger.warning("Missing session_id in 2FA completion request.")
            return jsonify({'error': "Missing session_id."}), 400

        # Validate session_id exists
        from services.fidelity import two_fa_sessions, complete_2fa_and_trade
        from services.chase import two_fa_sessions as chase_two_fa_sessions, complete_2fa_and_trade as chase_complete_2fa_and_trade
        from services.schwab import two_fa_sessions as schwab_two_fa_sessions, complete_2fa_and_trade as schwab_complete_2fa_and_trade
        from services.firstrade import two_fa_sessions as firstrade_two_fa_sessions, complete_2fa_and_trade as firstrade_complete_2fa_and_trade
        from services.wellsfargo import two_fa_sessions as wells_two_fa_sessions, complete_2fa_and_trade as wells_complete_2fa_and_trade
        from services.webull import two_fa_sessions as webull_two_fa_sessions, complete_2fa_and_trade as webull_complete_2fa_and_trade
        from services.public import two_fa_sessions as public_two_fa_sessions, complete_2fa_and_trade as public_complete_2fa_and_trade
        from services.robinhood import two_fa_sessions as rh_two_fa_sessions, complete_2fa_and_trade as rh_complete_2fa_and_trade
        from services.fennel import two_fa_sessions as fennel_two_fa_sessions, complete_2fa_and_trade as fennel_complete_2fa_and_trade

        logger.info(f"Received session ID for 2FA completion: {session_id}")

        if session_id in two_fa_sessions:
            trade_response = complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in chase_two_fa_sessions:
            trade_response = chase_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in schwab_two_fa_sessions:
            trade_response = schwab_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in firstrade_two_fa_sessions:
            trade_response = firstrade_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in public_two_fa_sessions:
            trade_response = public_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in wells_two_fa_sessions:
            trade_response = wells_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in webull_two_fa_sessions:
            trade_response = webull_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in rh_two_fa_sessions:
            trade_response = rh_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        elif session_id in fennel_two_fa_sessions:
            trade_response = fennel_complete_2fa_and_trade(
                session_id=session_id,
                two_fa_code=two_fa_code
            )
        else:
            logger.warning(f"Invalid session_id: {session_id}")
            return jsonify({'error': 'Invalid session_id.'}), 400

        return jsonify(trade_response), 200

    except Exception as e:
        logger.error(f"Error processing 2FA completion request: {str(e)}")
        return jsonify({'error': 'An error occurred while completing 2FA.'}), 500
