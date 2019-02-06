# 1) export your login password out from this script
#export DREG_LOGIN=...
#export DREG_PWD=...

# 2) set host
DREG_HOST=
DREG_URL="$DREG_HOST/v2/_catalog"

# SCRIPT START

# Save the response headers of our first request to the registry to get the Www-Authenticate header
respHeader=$(tempfile);
curl -k --dump-header $respHeader "$DREG_URL"

# Extract the realm, the service, and the scope from the Www-Authenticate header
wwwAuth=$(cat $respHeader | grep "Www-Authenticate")
realm=$(echo $wwwAuth | grep -o '\(realm\)="[^"]*"' | cut -d '"' -f 2)
service=$(echo $wwwAuth | grep -o '\(service\)="[^"]*"' | cut -d '"' -f 2)
scope=$(echo $wwwAuth | grep -o '\(scope\)="[^"]*"' | cut -d '"' -f 2)
echo "realm: $realm, service: $service, scope: $scope"

# Query the auth server to get a token
#-H "Authorization: Basic $(echo -n "vgreiner:GLE_REG_PWD" | base64)"
token=$(curl -H "service: $service" -H "scope: $scope" -H "offline_token: true" -u $DREG_LOGIN:$DREG_PWD $realm | jq -r '.token')
echo "token: $token"

# Query the registry again, but this time with a bearer token
curl -vk -H "Authorization: Bearer $token" $DREG_URL
