# OrchestratorAPI

All URIs are relative to *https://fountain.coach*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batchDeploy**](OrchestratorAPI.md#batchdeploy) | **POST** /v1/deploy | Batch Deploy
[**createService**](OrchestratorAPI.md#createservice) | **POST** /v1/services | Create Service
[**deleteService**](OrchestratorAPI.md#deleteservice) | **DELETE** /v1/services/{service} | Delete Service
[**deployService**](OrchestratorAPI.md#deployservice) | **POST** /v1/services/{service}/deploy | Deploy Service
[**getConfig**](OrchestratorAPI.md#getconfig) | **GET** /v1/services/{service}/config | Get Config
[**getLogs**](OrchestratorAPI.md#getlogs) | **GET** /v1/services/{service}/logs | Get Logs
[**getService**](OrchestratorAPI.md#getservice) | **GET** /v1/services/{service} | Get Service
[**health**](OrchestratorAPI.md#health) | **GET** /v1/health | Health
[**listServices**](OrchestratorAPI.md#listservices) | **GET** /v1/services | List Services
[**patchConfig**](OrchestratorAPI.md#patchconfig) | **PATCH** /v1/services/{service}/config | Patch Config
[**rollbackService**](OrchestratorAPI.md#rollbackservice) | **POST** /v1/services/{service}/rollback | Rollback Service


# **batchDeploy**
```swift
    open class func batchDeploy(deployRequest: DeployRequest, completion: @escaping (_ data: BatchDeployResponse?, _ error: Error?) -> Void)
```

Batch Deploy

Accepts a list of service names in `request.services`.   Returns a BatchDeployResponse with an array of DeployResponse objects.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let deployRequest = DeployRequest(services: ["services_example"]) // DeployRequest | 

// Batch Deploy
OrchestratorAPI.batchDeploy(deployRequest: deployRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deployRequest** | [**DeployRequest**](DeployRequest.md) |  | 

### Return type

[**BatchDeployResponse**](BatchDeployResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createService**
```swift
    open class func createService(name: String, serviceSpec: ServiceSpec, completion: @escaping (_ data: ServiceDetail?, _ error: Error?) -> Void)
```

Create Service

Create a new service.   - **name** (query parameter): unique service name   - **spec** (JSON body): details conforming to ServiceSpec

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let name = "name_example" // String | Name
let serviceSpec = ServiceSpec(image: "image_example", ports: "TODO", secrets: ["secrets_example"], configs: [ConfigReference(name: "name_example", target: "target_example")]) // ServiceSpec | 

// Create Service
OrchestratorAPI.createService(name: name, serviceSpec: serviceSpec) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **String** | Name | 
 **serviceSpec** | [**ServiceSpec**](ServiceSpec.md) |  | 

### Return type

[**ServiceDetail**](ServiceDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteService**
```swift
    open class func deleteService(service: String, completion: @escaping (_ data: Void?, _ error: Error?) -> Void)
```

Delete Service

Delete a service by name. Returns HTTP 204 on success.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Delete Service
OrchestratorAPI.deleteService(service: service) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 

### Return type

Void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deployService**
```swift
    open class func deployService(service: String, deployRequest: DeployRequest, completion: @escaping (_ data: DeployResponse?, _ error: Error?) -> Void)
```

Deploy Service

Trigger a deployment for the specified service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 
let deployRequest = DeployRequest(services: ["services_example"]) // DeployRequest | 

// Deploy Service
OrchestratorAPI.deployService(service: service, deployRequest: deployRequest) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 
 **deployRequest** | [**DeployRequest**](DeployRequest.md) |  | 

### Return type

[**DeployResponse**](DeployResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getConfig**
```swift
    open class func getConfig(service: String, completion: @escaping (_ data: ConfigDetail?, _ error: Error?) -> Void)
```

Get Config

Retrieve the current config (env & ports) for the specified service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Get Config
OrchestratorAPI.getConfig(service: service) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 

### Return type

[**ConfigDetail**](ConfigDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getLogs**
```swift
    open class func getLogs(service: String, tail: Int? = nil, completion: @escaping (_ data: String?, _ error: Error?) -> Void)
```

Get Logs

Return the last `tail` lines of logs for the given service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 
let tail = 987 // Int | Tail (optional) (default to 100)

// Get Logs
OrchestratorAPI.getLogs(service: service, tail: tail) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 
 **tail** | **Int** | Tail | [optional] [default to 100]

### Return type

**String**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getService**
```swift
    open class func getService(service: String, completion: @escaping (_ data: ServiceDetail?, _ error: Error?) -> Void)
```

Get Service

Fetch detailed information about a single service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Get Service
OrchestratorAPI.getService(service: service) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 

### Return type

[**ServiceDetail**](ServiceDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health**
```swift
    open class func health(completion: @escaping (_ data: HealthResponse?, _ error: Error?) -> Void)
```

Health

Returns {\"status\":\"ok\",\"uptime\":\"XhYmZs\"}.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient


// Health
OrchestratorAPI.health() { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**HealthResponse**](HealthResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listServices**
```swift
    open class func listServices(limit: Int? = nil, offset: Int? = nil, status: String? = nil, completion: @escaping (_ data: ServiceListResponse?, _ error: Error?) -> Void)
```

List Services

Retrieve a paginated list of services. Optional filter on `status` if provided.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let limit = 987 // Int | Limit (optional) (default to 50)
let offset = 987 // Int | Offset (optional) (default to 0)
let status = "status_example" // String | Status (optional)

// List Services
OrchestratorAPI.listServices(limit: limit, offset: offset, status: status) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Int** | Limit | [optional] [default to 50]
 **offset** | **Int** | Offset | [optional] [default to 0]
 **status** | **String** | Status | [optional] 

### Return type

[**ServiceListResponse**](ServiceListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patchConfig**
```swift
    open class func patchConfig(service: String, configPatch: ConfigPatch, completion: @escaping (_ data: ConfigDetail?, _ error: Error?) -> Void)
```

Patch Config

Partially update the service configuration. Only the fields provided in ConfigPatch will be modified.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 
let configPatch = ConfigPatch(env: "TODO", ports: "TODO") // ConfigPatch | 

// Patch Config
OrchestratorAPI.patchConfig(service: service, configPatch: configPatch) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 
 **configPatch** | [**ConfigPatch**](ConfigPatch.md) |  | 

### Return type

[**ConfigDetail**](ConfigDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rollbackService**
```swift
    open class func rollbackService(service: String, completion: @escaping (_ data: DeployResponse?, _ error: Error?) -> Void)
```

Rollback Service

Initiate a rollback for the specified service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Rollback Service
OrchestratorAPI.rollbackService(service: service) { (response, error) in
    guard error == nil else {
        print(error)
        return
    }

    if (response) {
        dump(response)
    }
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **String** |  | 

### Return type

[**DeployResponse**](DeployResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

