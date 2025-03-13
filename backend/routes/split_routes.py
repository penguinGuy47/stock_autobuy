from flask import Blueprint, jsonify, request
from controllers.split_controller import SplitController
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

splits_bp = Blueprint('splits', __name__)

@splits_bp.route('/splits/reverse-splits', methods=['GET'])
def get_reverse_splits():
    """API endpoint to get reverse splits data with support for incremental updates"""
    logger.info(f"Received reverse splits request: {request.url}")
    logger.info(f"Query parameters: {request.args}")

    try:
        # Use the controller to handle the request
        response_data, status_code = SplitController.get_reverse_splits(request.args)
        
        logger.info(f"Returning response with status code {status_code}")
        return jsonify(response_data), status_code
    except Exception as e:
        logger.error(f"Error in route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Failed to fetch reverse splits data'}), 500
