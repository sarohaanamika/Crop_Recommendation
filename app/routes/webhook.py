from flask import Blueprint, request, jsonify, current_app
import hmac
import hashlib
import os
import logging

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/github-webhook', methods=['POST'])
def github_webhook():
    """
    GitHub webhook for CI/CD automation
    Demonstrates DevOps practice: Automatic deployments on code changes
    """
    try:
        # Verify the webhook secret (basic DevSecOps practice)
        secret = os.getenv('WEBHOOK_SECRET', '')
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Log webhook receipt for monitoring
        current_app.logger.info(f"📦 Webhook received: {request.headers.get('X-GitHub-Event')}")
        
        if secret and signature:
            # Verify webhook signature (security best practice)
            body = request.get_data()
            expected_signature = 'sha256=' + hmac.new(
                secret.encode(), body, hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                current_app.logger.warning("🔒 Webhook signature verification failed")
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Process GitHub events
        event_type = request.headers.get('X-GitHub-Event', '')
        
        if event_type == 'ping':
            current_app.logger.info("✅ Webhook ping received - configuration valid")
            return jsonify({
                'message': 'Webhook configured successfully!',
                'event': 'ping',
                'status': 'active'
            }), 200
        
        elif event_type == 'push':
            # This is where you'd trigger your CI/CD pipeline
            commit_id = request.json.get('head_commit', {}).get('id', '')[:7]
            current_app.logger.info(f'🚀 Deployment triggered by push: {commit_id}')
            return jsonify({
                'message': 'CI/CD pipeline triggered',
                'event': 'push',
                'commit': commit_id,
                'action': 'deployment_started'
            }), 200
        
        elif event_type == 'pull_request':
            action = request.json.get('action', '')
            current_app.logger.info(f'🔀 Pull request {action} received')
            return jsonify({
                'message': f'Pull request {action}',
                'event': 'pull_request',
                'action': action
            }), 200
        
        return jsonify({
            'message': 'Webhook received',
            'event': event_type,
            'status': 'processed'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Webhook error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500