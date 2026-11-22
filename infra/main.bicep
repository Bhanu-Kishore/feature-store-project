@description('Azure region. The student subscription policy allows centralindia, koreacentral, indonesiacentral, malaysiawest and uaenorth.')
param location string = 'centralindia'

@description('Short name prefix used for all resources.')
param prefix string = 'churn'

@description('Minimum Container Apps replicas. 0 keeps idle cost at zero (cold starts apply).')
@minValue(0)
@maxValue(5)
param minReplicas int = 0

@description('Maximum Container Apps replicas.')
@minValue(1)
@maxValue(10)
param maxReplicas int = 1

var suffix = uniqueString(resourceGroup().id)
var acrName = toLower('${prefix}acr${suffix}')
var storageName = toLower('${prefix}st${suffix}')
var logName = '${prefix}-logs-${suffix}'
var envName = '${prefix}-env-${suffix}'
var apiName = '${prefix}-api-${suffix}'
var webName = '${prefix}-web-${suffix}'

resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    // Admin credentials are used by the Container Apps to pull images. They are
    // stored only as encrypted Container App secrets, never in source control.
    adminUserEnabled: true
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource assetsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'assets'
  properties: {
    publicAccess: 'None'
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource feastShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  parent: fileService
  name: 'feast-data'
  properties: {
    accessTier: 'TransactionOptimized'
    shareQuota: 1
  }
}

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource env 'Microsoft.App/managedEnvironments@2026-07-01' = {
  name: envName
  location: location
  properties: {
    // Standard consumption environment. New environments default to "Express",
    // which does not support Azure Files mounts or system-assigned identities.
    environmentMode: 'ConsumptionOnly'
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource feastVolume 'Microsoft.App/managedEnvironments/storages@2026-07-01' = {
  parent: env
  name: 'feastdata'
  properties: {
    azureFile: {
      accountName: storage.name
      accountKey: storage.listKeys().keys[0].value
      shareName: feastShare.name
      accessMode: 'ReadWrite'
    }
  }
}

resource webApp 'Microsoft.App/containerApps@2026-07-01' = {
  name: webName
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
        transport: 'auto'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'web'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/'
                port: 80
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2026-07-01' = {
  name: apiName
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        transport: 'auto'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'FEAST_REPO_PATH'
              value: '/app'
            }
            {
              name: 'MODEL_PATH'
              value: '/app/model'
            }
            {
              name: 'CORS_ORIGINS'
              value: 'https://${webApp.properties.configuration.ingress.fqdn},http://localhost,http://127.0.0.1,http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173'
            }
          ]
          volumeMounts: [
            {
              volumeName: 'feast-data'
              mountPath: '/app/data'
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 15
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 45
              periodSeconds: 30
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      volumes: [
        {
          name: 'feast-data'
          storageType: 'AzureFile'
          storageName: feastVolume.name
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output resourceGroupName string = resourceGroup().name
output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output containerAppName string = app.name
output frontendAppName string = webApp.name
output containerAppEnvironment string = env.name
output storageAccountName string = storage.name
output backendUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
output frontendUrl string = 'https://${webApp.properties.configuration.ingress.fqdn}'
output logAnalyticsWorkspace string = logs.name
