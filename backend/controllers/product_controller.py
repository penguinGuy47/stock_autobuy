from flask import Blueprint, request, jsonify
import logging
from services.bestbuy import run_product_automation

product_bp = Blueprint('product_bp', __name__)
logger = logging.getLogger(__name__)

@product_bp.route('/automate_product', methods=['POST'])
def automate_product():
    try:
        data = request.json
        # Expecting keys: taskName (for labeling), billing (used here as the product SKU), 
        # site (e.g., "bestbuy"), and profile (an object/dict with at least 'username' and 'password')
        task_name = data.get('taskName')
        sku = data.get('billing')  # using billing field as SKU
        site = data.get('site')
        profile = data.get('profile')

        if not task_name or not sku or not site or not profile:
            return jsonify({'error': 'Missing required parameters.'}), 400

        if site.lower() != 'bestbuy':
            return jsonify({'error': f"Automation for site '{site}' is not implemented."}), 400

        # Call the modified BestBuy automation function.
        response = run_product_automation(profile, sku)
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in product automation: {str(e)}")
        return jsonify({'error': 'An error occurred during product automation.'}), 500
