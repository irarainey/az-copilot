#!/bin/bash
set -euo pipefail

# Create a unique name for the resources
CURRENT_SUBSCRIPTION_ID=$(az account show --query "id" -o tsv)
TIMESTAMP_SALT=$(date '+%s')
UNIQUE_SUFFIX=$(echo "$CURRENT_SUBSCRIPTION_ID$TIMESTAMP_SALT" | shasum | cut -c 1-12)

# Edit this to change the name of the resources deployed
NAME="az-cp-$UNIQUE_SUFFIX"

# Edit this to set the location for the resources
LOCATION="uksouth"

# Run the Bicep deployment
az deployment sub create \
            --template-file ./infrastructure/bicep/main.bicep \
            --location $LOCATION \
            --name "deploy-az-copilot-$NAME" \
            --parameters \
                resourceGroupName="$NAME" \
                openaiName="$NAME" \
                searchName="$NAME"

# Get the API key for the OpenAI resource
API_KEY=$(az cognitiveservices account keys list \
            --name "$NAME" \
            --resource-group "$NAME" \
            --query "key1" \
            -o tsv)

# Get the admin key for the Cognitive Search resource
COG_KEY=$(az search admin-key show \
            --resource-group "$NAME" \
            --service-name "$NAME" \
            --query "primaryKey" \
            -o tsv)

# Display the configuration values
echo -e "\nDeployment complete"
echo -e "\nUse these values to configure Copilot:\n"
echo -e "OpenAI Endpoint: https://$NAME.openai.azure.com/"
echo -e "OpenAI API Key: $API_KEY"
echo -e "OpenAI Completion Model Name: copilot"
echo -e "OpenAI Embedding Model Name: copliot-embedding"
echo -e "Cognitive Search Endpoint: https://$NAME.search.windows.net"
echo -e "Cognitive Search Admin Key: $COG_KEY"
