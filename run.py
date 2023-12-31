import os
from   flask_migrate import Migrate
from   flask_minify  import Minify
from   sys import exit
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from apps.config import config_dict
from apps import create_app, db
from apps.utils.models import Users,Members, GlobalValues, Shares, Loan, ThriftFunds


# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

admin = Admin(app, name='Dashboard')
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Members, db.session))
admin.add_view(ModelView(GlobalValues, db.session))
admin.add_view(ModelView(Shares, db.session))
admin.add_view(ModelView(Loan   , db.session))
admin.add_view(ModelView(ThriftFunds   , db.session))





if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('FLASK_ENV        = ' + os.getenv('FLASK_ENV') )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

if __name__ == "__main__":
    app.run()
    