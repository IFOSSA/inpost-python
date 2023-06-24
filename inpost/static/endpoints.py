# AUTH #
login_url: str = "https://api-inmobile-pl.easypack24.net/v1/authenticate"
send_sms_code_url: str = "https://api-inmobile-pl.easypack24.net/v1/sendSMSCode/"  # get
confirm_sms_code_url: str = "https://api-inmobile-pl.easypack24.net/v1/confirmSMSCode"  # post
logout_url: str = "https://api-inmobile-pl.easypack24.net/v1/logout"  # post
refresh_token_url: str = "https://api-inmobile-pl.easypack24.net/v1/authenticate"  # post

# INCOMING PARCELS #
tracked_url: str = "https://api-inmobile-pl.easypack24.net/v3/parcels/tracked/"  # get
multi_url: str = "https://api-inmobile-pl.easypack24.net/v3/parcels/multi/"  # get
collect_url: str = "https://api-inmobile-pl.easypack24.net/v1/collect/validate"  # post
reopen_url: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/reopen"  # post
compartment_open_url: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/open"  # post
compartment_status_url: str = "https://api-inmobile-pl.easypack24.net/v1/collect/compartment/status"  # post
terminate_collect_session_url: str = "https://api-inmobile-pl.easypack24.net/v1/collect/terminate"  # post
shared_url: str = "https://api-inmobile-pl.easypack24.net/v1/parcels/shared"  # post

# CREATING PARCEL #
create_url: str = "https://api-inmobile-pl.easypack24.net/v1/parcels"
points_url: str = "https://api-inmobile-pl.easypack24.net/v3/points"
blik_status_url: str = "https://api-inmobile-pl.easypack24.net/v1/payments/blik/alias/status"
create_blik_url: str = "https://api-inmobile-pl.easypack24.net/v1/payments/transactions/create/blik"

# OUTGOING PARCELS #
sent_url: str = "https://api-inmobile-pl.easypack24.net/v2/parcels/sent/"  # get
parcel_points_url: str = "https://api-inmobile-pl.easypack24.net/v3/points/"  # get
validate_sent_url: str = "https://api-inmobile-pl.easypack24.net/v1/send/validate/"  # post
open_sent_url: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/open"  # post
reopen_sent_url: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/reopen"  # post
status_sent_url: str = "https://api-inmobile-pl.easypack24.net/v1/send/compartment/status"  # post
confirm_sent_url: str = "https://api-inmobile-pl.easypack24.net/v1/send/confirm"  # post
parcel_prices_url: str = "https://api-inmobile-pl.easypack24.net/v1/prices/parcels"  # get

# RETURNS #
returns_url: str = "https://api-inmobile-pl.easypack24.net/v1/returns/parcels/"  # get
tickets_url: str = "https://api-inmobile-pl.easypack24.net/v1/returns/tickets"  # get
parcel_notifications_url: str = "https://api-inmobile-pl.easypack24.net/v2/notifications?type=PUSH%2CNEWS%2CTILE"  # get

# FRIENDS #
friendship_url: str = "https://api-inmobile-pl.easypack24.net/v1/friends/"  # get, post, patch, delete
validate_friendship_url: str = "https://api-inmobile-pl.easypack24.net/v1/invitations/validate"  # post
accept_friendship_url: str = "https://api-inmobile-pl.easypack24.net/v1/invitations/accept"  # post
