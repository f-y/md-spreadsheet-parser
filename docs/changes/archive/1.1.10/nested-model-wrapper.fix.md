Fixed nested models in NPM package constructors to properly wrap child elements.

- Sheet constructor now wraps tables array items as Table instances
- Workbook constructor now wraps sheets array items as Sheet instances
- This ensures `json` getter recursively returns objects with proper metadata types
- Previously, nested metadata was returned as strings instead of objects
