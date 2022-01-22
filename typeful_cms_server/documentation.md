# Creation Model
### Question:
- How do we make model creation make sense from an api perspective?
    - JSON object representing an object?
    - How do we validate the type on the backend?
    - What kind of types do we allow for? Singletons?
### Answer:
Models will be defined as a set of predefined "typeful_cms" types which are
really just python models presented to the front end as if they're distinct. An
adaptor layer will exist between these models and the DB. The model set will be
as follows:

- text
- enumeration
- image/images/media
- number
- boolean
- json_object

An abstraction layer will exist that can take pure json objects and translate
them to SQL storable objects
```
  {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "address": {
      "street": "Kulas Light",
      "suite": "Apt. 556",
      "city": "Gwenborough",
      "zipcode": "92998-3874",
      "geo": {
        "lat": "-37.3159",
        "lng": "81.1496",
        "city": {
          "name" : "england",
          "state": "hello"
        }
      }
    },
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
      "name": "Romaguera-Crona",
      "catchPhrase": "Multi-layered client-server neural-net",
      "bs": "harness real-time e-markets"
    }
  }
```