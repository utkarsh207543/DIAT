from flask import render_template, request, redirect, url_for, session, flash
import os

def setup_routes(app, google_auth, db_manager):
    """Set up routes for the application"""
    
    @app.route('/login')
    def login():
        """Login page"""
        return render_template('login.html', google_client_id=os.environ.get('GOOGLE_CLIENT_ID'))
    
    @app.route('/auth/google')
    def google_login():
        """Initiate Google OAuth"""
        try:
            authorization_url, state = google_auth.get_authorization_url()
            session['oauth_state'] = state
            print(f"🔗 Redirecting to Google OAuth: {authorization_url}")
            return redirect(authorization_url)
        except Exception as e:
            print(f"❌ Google OAuth error: {str(e)}")
            flash(f'OAuth configuration error: {str(e)}', 'error')
            return redirect(url_for('login'))
