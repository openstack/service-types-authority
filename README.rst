=======================
Service Types Authority
=======================

The following is a central authority for handing out service types to
projects for their services.

Each OpenStack service with a REST API must have a well known service type.
The well known service type guarantees a documented API is available
for that service. Users of this service can trust that it will be the
same between different OpenStack environments.

Attributes
==========

The following attributes are required for a service type registration:

service-type (required)
-----------------------

The unique identifier for the service to be used in the service catalog.

project (required)
------------------

The name of the OpenStack project that contains the definition of the API
claimed by this service type. OpenStack project source code is found in
`https://opendev.org/openstack/{project}`. If the API reference docs are
not found in the project repository, the `api_reference_project` field can be
used to indicate the repository in which they are found.

api_reference (required)
------------------------

A published API reference document for the API identified by this
service type. If not specified in the source yaml file, it will be generated
as `https://docs.openstack.org/api-ref/{service-type}/`.

api_reference_project (optional)
--------------------------------

An OpenStack git project holding the source code for the project's API
reference.

description (optional)
----------------------

A short description about the service in question. It helps people
reading only this document.

aliases (optional)
------------------

An ordered list of historical aliases for this service type.

.. note:: The list of aliases is **only** for communicating the existing
          set of other names that services have gone by from the time before
          this list existed. Changing a ``service-type`` is **VERY BAD** and
          breaks users. It's important to list them so that everyone can
          share in the knowledge of what to do with the clouds that are out
          there, but seriously, putting things here is only for documenting
          history, not for making new changes.

A service must have one and only one known service type. However,
there are older names that have been commonly used for some services. In
order for API consumers to be able to count on the Service Types Authority
service-type as an inbound interface they expect, ``aliases`` provides a
ordered list of known fallback names. If an API consumer cannot find a given
``service-type`` in the ``service-catalog``, they are directed to try the
list of ``aliases`` here, in the order they are given, in order to find
the requested endpoint.

secondary (optional)
--------------------

If secondary is set and is true, the project is not the primary service people
associate with the project codename. For instance, the ``nova`` project has
two services, ``compute`` and ``placement``. ``compute`` is the primary
project. ``placement`` is secondary.

Naming
======

.. note:: Established service types need not be forcefully retrofitted
          to conform to these guidelines. For this reason you may see
          entries such as ``ec2-api`` (contains a digit) or
          ``clustering`` (an action, not a thing).

New service type names should:

- Be English words
- Match the regex ``^[a-z][a-z-]*[a-z]$``.
- Be meaningful
- Not use terms which are incredibly overloaded in OpenStack space
  (e.g. policy)
- Be a thing, not an action (e.g. load-balancer, not load-balancing)
- Be singular instead of plural (e.g. image, not images)
- Be unversioned (e.g. volume, not volumev2)

Non Official Types in Service Catalog
=====================================

The OpenStack Service Catalog can be used for listing services outside
of the standardized service types. There will be no official registry
of these types, so conflicts are possible. As such, the types should
include an org prefix '$org:' where $org is something recognizable to
a particular organization and not part of the OpenStack ecosystem.
