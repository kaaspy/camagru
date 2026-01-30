#!/bin/bash

#No domain name registration to send mail from
#Using mailpit to intercept mails 
docker run -p 1025:1025 -p 8025:8025 \
-e MP_SMTP_AUTH="camagru:password123" \
-e MP_SMTP_AUTH_ALLOW_INSECURE=true \
-e MP_STMP_VERBOSE=true \
 axllent/mailpit
