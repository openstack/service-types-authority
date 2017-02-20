=======================
Service Types Authority
=======================

The following is a central authority for handing out service types to
projects.

OpenStack Projects with REST APIs must have a well known service type.
The well known service type guarantees a documented API is available
for that service. Users of this service can trust that it will be the
same between different OpenStack environments.

Attributes
==========

The following attributes are required for a service type registration:

project (required)
------------------

An OpenStack git project that contains the definition of the API
claimed by this service type. This is assumed to be a code repository,
though if multiple projects are implementing the same API they can
choose to have this be an API definition repository instead.

Project is a singleton and defines the reference point for the API in
question.

api_reference (required)
------------------------

A published API reference document for the API identified by this
service type.

description (optional)
----------------------

A short description about the service in question. It helps people
reading only this document.

Naming
======

Service types should be:

- English words
- Be matched by the regex [a-z\-]+
- Be meaningful
- Not use terms which are incredibly overloaded in OpenStack space
  (i.e. policy)
- A thing, not an action (i.e. load-balancer, not load-balancing)

Non Official Types in Service Catalog
=====================================

The OpenStack Service Catalog can be used for listing services outside
of the standardized service types. There will be no official registry
of these types, so conflicts are possible. As such, the types should
include an org prefix '$org:' where $org is something recognizable to
a particular organization and not part of the OpenStack ecosystem.
