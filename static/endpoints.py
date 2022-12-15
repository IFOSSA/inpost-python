login: str = 'https://api-inmobile-pl.easypack24.net/v1/authenticate'
send_sms_code: str = 'https://api-inmobile-pl.easypack24.net/v1/sendSMSCode/'  # get
confirm_sms_code: str = 'https://api-inmobile-pl.easypack24.net/v1/confirmSMSCode'  # post
logout: str = 'https://api-inmobile-pl.easypack24.net/v1/logout'  # post

# \/ Secured by JWT \/

refresh_token: str = 'https://api-inmobile-pl.easypack24.net/v1/authenticate'  # post
parcels: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/tracked'  # get
