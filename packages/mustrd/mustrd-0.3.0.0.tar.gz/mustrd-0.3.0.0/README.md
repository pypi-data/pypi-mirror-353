# mustrd


[<img src="https://github.com/Semantic-partners/mustrd/raw/python-coverage-comment-action-data/badge.svg?sanitize=true" alt="coverage badge">](https://github.com/Semantic-partners/mustrd/tree/python-coverage-comment-action-data)

### Why?

How do you know your SPARQL, whether it's in a pipeline, or a query, is doing what you intend? 

As much as we love RDF and SPARQL and Semantic Tech in general, we found a small gap in tooling to give us that certainty. 

We missed the powerful testing frameworks that have evolved in imperative languages that help ensure you've written code that does what you think it should. 

We wanted to be able to

* setup data scenarios and ensure queries worked as expected
* setup edge cases for queries and ensure they still work
* isolate small sparql enrichment / transformation steps and know we're only INSERTing what we intend

Enter MustRD. 

### What?

MustRD is a Spec-By-Example ontology, with a reference python implementation, inspired by the likes of Cucumber. 

It's designed to be triplestore/SPARQL engine agnostic (aren't open standards *wonderful*!). 

### What it is NOT
MustRD is nothing to do with SHACL, or an alternative to it. In fact, we use SHACL for some of our features. 

SHACL provides validation around data. 

MustRD provides validation around data transformations. 

### How?
You define your specs in ttl, or trig files. 
We use the SBE approach of *Given*, *When*, *Then* to define starting dataset, an action, and a set of expectations. We build up a set of data. 
Then, depending on whether your SPARQL is a CONSTRUCT, SELECT or a INSERT/DELETE, we run it, and compare results against a set of expectations (*Then*) that are defined in the same way as a *Given* .
Alternatively, you could define your *Then*

* as an explicit ASK, or
* select; or 
* in a higher-order expectation language like you will be used to in various platforms, a set of expectations.


### When?

Soon. It's a work in progress, and we're building the things *we* need for the projects we work on at multiple clients, with multiple vendor stacks. 
We already think it's useful, but it might not meet *your* needs, out of the box. 

We invite you to try it, see where it doesn't fit, and raise an issue, or even better, a PR! If you need something custom, please check out our consultancy rates, and we might be able to prioritise a new feature for you.

## Support
We're a specialist consultancy in Semantic Tech, we're putting this out in case it's useful, but if you need more support, kindly contact our business team on info@semanticpartners.com, or mustrd@semanticpartners.com

