import os
secretkey = os.environ['progressbot_discordapikey']  # this one for the real chat room

test_environment = os.environ['progressbot_test_environment']
command_prefix = os.environ['progressbot_command_prefix']

master_config = "test"  # used for timezone calculations

db_secrets = [os.environ['progressbot_db_username'], os.environ['progressbot_db_password']] # db config for storage for vacuum.py
server= {
    'ip':os.environ['progressbot_server_ip'],
    'password': os.environ['progressbot_server_password'],
}

minecraft_db = os.environ['progressbot_minecraft_db']

global_ignore_list = os.environ['progressbot_global_ignore_list']

mc_scripts_path = os.environ['progressbot_mc_base_path'] + "scripts/"