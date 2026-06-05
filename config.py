import os
secretkey = os.environ['progressbot_discordapikey']  # this one for the real chat room

test_environment = os.environ['progressbot_test_environment']
command_prefix = os.environ['progressbot_command_prefix']

db_secrets = {
    'username': os.environ['progressbot_db_username'],
    'password': os.environ['progressbot_db_password'],
    'port': os.environ['progressbot_db_port'],
    'host': os.environ['progressbot_db_host'],
    'database': os.environ['progressbot_db_database']
} # db config
global_ignore_list = os.environ['progressbot_global_ignore_list']