#!/bin/sh

# Replace environment variables in built files
# This allows runtime configuration of the React app

echo "Configuring environment variables..."

# Default values if not provided
REACT_APP_API_URL=${REACT_APP_API_URL:-"http://localhost:5000"}
REACT_APP_ENVIRONMENT=${REACT_APP_ENVIRONMENT:-"production"}
REACT_APP_STRIPE_PUBLIC_KEY=${REACT_APP_STRIPE_PUBLIC_KEY:-""}
REACT_APP_ANALYTICS_ID=${REACT_APP_ANALYTICS_ID:-""}

# Replace placeholders in the built JavaScript files
find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REACT_APP_API_URL_PLACEHOLDER|$REACT_APP_API_URL|g" {} \;
find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REACT_APP_ENVIRONMENT_PLACEHOLDER|$REACT_APP_ENVIRONMENT|g" {} \;
find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REACT_APP_STRIPE_PUBLIC_KEY_PLACEHOLDER|$REACT_APP_STRIPE_PUBLIC_KEY|g" {} \;
find /usr/share/nginx/html -name "*.js" -exec sed -i "s|REACT_APP_ANALYTICS_ID_PLACEHOLDER|$REACT_APP_ANALYTICS_ID|g" {} \;

echo "Environment configuration complete."
echo "API URL: $REACT_APP_API_URL"
echo "Environment: $REACT_APP_ENVIRONMENT"

# Execute the main command
exec "$@"

