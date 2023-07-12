from flask import Blueprint

# Initialize a Blueprint object for the authentication routes
blueprint = Blueprint(
    'authentication_blueprint',  # blueprint name
    __name__,  # module where blueprint is defined
    url_prefix=''  # prefix to add to all routes registered with this blueprint
)
