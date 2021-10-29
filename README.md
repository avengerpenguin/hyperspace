# Hyperspace

General-purpose REST and hypermedia client written in Python.
Implements support for multiple hypermedia types using Mike Amundsen's
[H Factor](http://amundsen.com/hypermedia/hfactor/) model.

This is a bit experimental still and doesn't have broad support for as
many types as it could just yet.

## Concept

The ceonceptual view is to model any HTTP response that uses
hypermedia with some common objects. This is done by generalising HTML
somewhat (as HTML is the most familiar) such that we get the following
domain objects::

- The `Page` is the semantic model of each HTTP response. It comprises
  `data` in the form of an RDF graph for any semantic data found in
  the response. It also provides `links`, `queries` and `templates`
  for onward state transitions.
- A `Link` is the generalised form of the HTML anchor (LO or "Outbound
  Links" in the H Factor model). It usually has a `name` to identify
  it from other links in a page and then an `href` for a URL to take
  the clien to another `Page`.
- A `Query` is closest to an HTML form with the `GET` method. This is
  the LT factor in the H Factor model. It uses a `rel` to identify it
  from other potential queries in a page and a `uri_template` property
  that the client can expand with parameters.
- A `Template` provides the LN H Factor, i.e. non-idempotent updates.
  This generalises an HTML form with `POST` but with some work could
  be generalise to support the LI factor for idempotent updates too
  (`PUT` and `DELETE`). This hasn't been done yet as it is unlikely to
  be supported in HTML so will be added when more hypermedia types are
  added.


These objects are referred to as "affordances" since they provide
various things for clients to interact with.

## Usage


``` python
import hyperspace

page = hyperspace.jump('https://reddit.com/r/python')

```
