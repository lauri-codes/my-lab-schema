# NOMAD Schema Plugin for My Lab

This is a NOMAD schema plugin forked from
https://github.com/nomad-coe/nomad-schema-plugin-example. It is a simple
example how a custom lab workflow could be captured using a custom schema.

## Functionality
Provides a new entry type called `MySample`, which can be used to track samples
and measurements performed on them. This schema is based on the NOMAD base
class `Sample`. New fields are added for the UV-Vis data and the X-ray
fluorescence data that are reported in our lab workflow. Basic data is
pre-filled by the schema to minimize the need for typing.

## Registration
Add the following into the nomad.yaml configuration of your NOMAD Oasis:

```yaml
plugins:
  options:
    schemas/mylabschema:
      python_package: mylabschema
```


## Usage
- Create new upload
- Create new entry, select `MySample` as the schema
- Upload measurement data (UV-Vis + X-ray fluorescence)
- Save
