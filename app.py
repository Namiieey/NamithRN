from flask import Flask, render_template, request, jsonify
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__, static_folder='static')

# Configuration
DEBUG = True
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'your-email@example.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Set this in production environment

# Routes
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    data = request.get_json()
    
    # Validate form data
    if not all(key in data for key in ['name', 'email', 'subject', 'message']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Log the contact submission
    log_contact(data)
    
    # Send email notification
    if EMAIL_PASSWORD:  # Only attempt to send email if password is configured
        try:
            send_email_notification(data)
            return jsonify({'success': True, 'message': 'Your message has been sent!'}), 200
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")
            return jsonify({'success': False, 'message': 'Could not send email, but your message was logged'}), 500
    else:
        # If email sending is not configured, just return success for the logged message
        return jsonify({'success': True, 'message': 'Your message has been received!'}), 200

@app.route('/api/projects')
def projects():
    """API endpoint to get project information"""
    projects = [
        {
            'id': 1,
            'title': 'Semi-Humanoid Robot',
            'description': 'A Python-powered semi-humanoid robot capable of basic interactions and tasks.',
            'technologies': ['Python', 'IoT', 'Machine Learning'],
            'status': 'completed',
            'image': 'robot1.jpg'
        },
        {
            'id': 2,
            'title': 'Advanced Humanoid Robot',
            'description': 'Work in progress: A fully articulated humanoid robot with advanced AI capabilities and modern UI.',
            'technologies': ['Python', 'Computer Vision', 'UI/UX'],
            'status': 'in-progress',
            'image': 'robot2.jpg'
        }
    ]
    return jsonify(projects)

# Helper Functions
def log_contact(data):
    """Log contact form submissions to a file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Name: {data['name']}, Email: {data['email']}, Subject: {data['subject']}\n"
    
    os.makedirs('logs', exist_ok=True)
    with open('logs/contacts.log', 'a') as f:
        f.write(log_entry)

def send_email_notification(data):
    """Send an email notification for new contact submissions"""
    msg = EmailMessage()
    msg['Subject'] = f"New Website Contact: {data['subject']}"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS  # Send to yourself
    
    # Email content
    email_body = f"""
    You have received a new contact message from your website:
    
    Name: {data['name']}
    Email: {data['email']}
    Subject: {data['subject']}
    
    Message:
    {data['message']}
    
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    msg.set_content(email_body)
    
    # Connect to SMTP server and send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Custom error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)