targetScope = 'subscription'
param location string = deployment().location
param resourceGroupName string
param searchName string
param openaiName string

resource rg 'Microsoft.Resources/resourceGroups@2020-06-01' = {
  name: resourceGroupName
  location: location
}

module openAI './common/openai.bicep' = {
  name: 'openAI'
  scope: rg
  params: {
    location: location
    name: openaiName
    deployments: [
      {
        name: 'copilot'
        sku: {
          name: 'Standard'
          capacity: 120
        }
        properties: {
          model: {
            format: 'OpenAI'
            name: 'gpt-35-turbo-16k'
            version: '0613'
          }
          versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
          raiPolicyName: 'Microsoft.Default'
        }
      }
      {
        name: 'copilot-embedding'
        sku: {
          name: 'Standard'
          capacity: 120
        }
        properties: {
          model: {
            format: 'OpenAI'
            name: 'text-embedding-ada-002'
            version: '2'
          }
          versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
          raiPolicyName: 'Microsoft.Default'
        }
      }
    ]
  }
}

module cognitiveSearch './common/cognitive_search.bicep' = {
  name: 'cognitiveSearch'
  scope: rg
  params: {
    location: location
    name: searchName
  }
}

