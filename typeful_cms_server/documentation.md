### Creation Model
- How do we make model creation make sense from an api perspective?
    - Obviously, we need to submit a model of some variety
    - JSON object representing an object?
    - How do we validate the type on the backend?
    - What kind of types do we allow for? Singletons?
```
{ 
    "name": "<model_name>",
    "model_def" : [
        {"<prop_name>" : "<prop_type>"}
    ]
}
```