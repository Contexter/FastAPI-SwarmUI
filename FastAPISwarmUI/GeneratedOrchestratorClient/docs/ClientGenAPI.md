# ClientGenAPI

All URIs are relative to *https://fountain.coach*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getClientStatus**](ClientGenAPI.md#getclientstatus) | **GET** /v1/clientgen/status/{service} | Get Client Status
[**regenerateClient**](ClientGenAPI.md#regenerateclient) | **POST** /v1/clientgen/{service}/regenerate | Regenerate Client


# **getClientStatus**
```swift
    open class func getClientStatus(service: String, completion: @escaping (_ data: ClientStatusResponse?, _ error: Error?) -> Void)
```

Get Client Status

Return the current status of client SDK generation for the given service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Get Client Status
ClientGenAPI.getClientStatus(service: service) { (response, error) in
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

[**ClientStatusResponse**](ClientStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **regenerateClient**
```swift
    open class func regenerateClient(service: String, completion: @escaping (_ data: ClientStatusResponse?, _ error: Error?) -> Void)
```

Regenerate Client

Trigger regeneration of the client SDK for the given service.

### Example
```swift
// The following code samples are still beta. For any issue, please report via http://github.com/OpenAPITools/openapi-generator/issues/new
import OrchestratorClient

let service = "service_example" // String | 

// Regenerate Client
ClientGenAPI.regenerateClient(service: service) { (response, error) in
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

[**ClientStatusResponse**](ClientStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

