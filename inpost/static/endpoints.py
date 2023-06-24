# AUTH #
login: str = "https://api-inmobile-pl.easypack24.net/v1/authenticate"
send_sms_code: str = "https://api-inmobile-pl.easypack24.net/v1/sendSMSCode/"  # get
confirm_sms_code: str = "https://api-inmobile-pl.easypack24.net/v1/confirmSMSCode"  # post
logout: str = "https://api-inmobile-pl.easypack24.net/v1/logout"  # post
refresh_token: str = "https://api-inmobile-pl.easypack24.net/v1/authenticate"  # post

# INCOMING PARCELS #
parcels: str = "https://api-inmobile-pl.easypack24.net/v3/parcels/tracked"  # get
parcel: str = "https://api-inmobile-pl.easypack24.net/v3/parcels/tracked/"  # get
multi: str = "https://api-inmobile-pl.easypack24.net/v3/parcels/multi/"  # get
collect: str = "https://api-inmobile-pl.easypack24.net/v1/collect/validate"  # post
reopen: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/reopen"  # post
compartment_open: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/open"  # post
compartment_status: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/status"  # post
terminate_collect_session: str = "https://api-inmobile-pl.easypack24.net/v1/collect/terminate"  # post
shared: str = "https://api-inmobile-pl.easypack24.net/v1/parcels/shared"  # post

# CREATING PARCEL #
create: str = "https://api-inmobile-pl.easypack24.net/v1/parcels"
points: str = "https://api-inmobile-pl.easypack24.net/v3/points"
blik_status: str = "https://api-inmobile-pl.easypack24.net/v1/payments/blik/alias/status"
create_blik: str = "https://api-inmobile-pl.easypack24.net/v1/payments/transactions/create/blik"

# OUTGOING PARCELS #
# sent: str = 'https://api-inmobile-pl.easypack24.net/v3/parcels/sent/'  # get
sent: str = "https://api-inmobile-pl.easypack24.net/v2/parcels/sent/"  # get
parcel_points: str = "https://api-inmobile-pl.easypack24.net/v3/points/"  # get
validate_sent: str = "https://api-inmobile-pl.easypack24.net/v1/send/validate/"  # post
open_sent: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/open"  # post
reopen_sent: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/reopen"  # post
status_sent: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/status"  # post
confirm_sent: str = "https://api-inmobile-pl.easypack24.net/v1/send/confirm"  # post
parcel_prices: str = "https://api-inmobile-pl.easypack24.net/v1/prices/parcels"  # get

# RETURNS #
returns: str = "https://api-inmobile-pl.easypack24.net/v1/returns/parcels/"  # get
tickets: str = "https://api-inmobile-pl.easypack24.net/v1/returns/tickets"  # get
parcel_notifications: str = "https://api-inmobile-pl.easypack24.net/v2/notifications?type=PUSH%2CNEWS%2CTILE"  # get

# FRIENDS #
friendship: str = "https://api-inmobile-pl.easypack24.net/v1/friends/"  # get, post, patch, delete
validate_friendship: str = "https://api-inmobile-pl.easypack24.net/v1/invitations/validate"  # post
accept_friendship: str = "https://api-inmobile-pl.easypack24.net/v1/invitations/accept"  # post
