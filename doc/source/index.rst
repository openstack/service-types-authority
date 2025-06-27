.. include:: ../../README.rst

Service Data
============

Source Data
-----------

The :download:`Service Types Authority <service-types.yaml>` information is
maintained in YAML for ease of human interactions and so that comments can
be used if needed.

.. literalinclude:: service-types.yaml
    :language: yaml

It is described by a :download:`Service Types Authority Schema <schema.json>`.

.. literalinclude:: schema.json
    :language: json

Publication
-----------

The information is also transformed into a JSON format and published to
https://service-types.openstack.org/service-types.json for ease of machine
interactions. The published format is different than the source format.

The published format contains five keys.

version
  An ISO Format Date Time string of the build time in UTC.

sha
  The git sha from which the file was built.

service_types
  A list of all of the official service types.

forward
  A mapping of official service type to aliases. Only contains entries for
  services that have aliaes.

reverse
  A mapping of aliases to official service type.

primary_service_by_project
  A mapping of project names to the primary service associated with that
  project. Every project has only one primary service.

all_types_by_service_type
  A mapping of service type to a list containing the official service type
  and all of its aliases. Contains an entry for every service.

service_types_by_project
  A mapping of project name to a list of all service types associated with
  that project.

The published format is described by a
:download:`Service Types Authority Published Schema <published-schema.json>`.

.. literalinclude:: schema.json
    :language: json
