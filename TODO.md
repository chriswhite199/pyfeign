# TODO

1. Make defaults optional
    * default is a query param
    * Unless param is an object or Dict - in which case use as body
2. Config - Body serializer (defaults to passing Dict as-is to request(json=))
3. Config - Body deserializer (consumes JSON dict response)
4. Wrap response based upon return type of function
    * Response - http response
    * None - just assert success code (raise_for_status)
    * Dict / List - response.json()
    * str - response.text
5. Class decorator `@Pyfeign`
    * Allow configuration of baseurl, headers, cookies, params etc