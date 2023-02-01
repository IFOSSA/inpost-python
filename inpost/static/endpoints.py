login: str = 'https://api-inmobile-pl.easypack24.net/v1/authenticate'
send_sms_code: str = 'https://api-inmobile-pl.easypack24.net/v1/sendSMSCode/'  # get
confirm_sms_code: str = 'https://api-inmobile-pl.easypack24.net/v1/confirmSMSCode'  # post

# \/ Secured by JWT \/

refresh_token: str = 'https://api-inmobile-pl.easypack24.net/v1/authenticate'  # post
parcels: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/tracked'  # get
parcel: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/tracked/'  # get
multi: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/multi/'  # get
collect: str = 'https://api-inmobile-pl.easypack24.net/v1/collect/validate'  # post
compartment_open: str = 'https://api-inmobile-pl.easypack24.net/v1/collect/compartment/open'  # post
compartment_status: str = 'https://api-inmobile-pl.easypack24.net/v1/collect/compartment/status'  # post
terminate_collect_session: str = 'https://api-inmobile-pl.easypack24.net/v1/collect/terminate'  # post
friends: str = 'https://api-inmobile-pl.easypack24.net/v1/friends/'  # get
shared: str = 'https://api-inmobile-pl.easypack24.net/v1/parcels/shared'  # post
sent: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/sent/'  # get
returns: str = 'https://api-inmobile-pl.easypack24.net/v1/returns/parcels/'  # get
parcel_prices: str = 'https://api-inmobile-pl.easypack24.net/v1/prices/parcels'  # get
tickets: str = 'https://api-inmobile-pl.easypack24.net/v1/returns/tickets'  # get
logout: str = 'https://api-inmobile-pl.easypack24.net/v1/logout'  # post
