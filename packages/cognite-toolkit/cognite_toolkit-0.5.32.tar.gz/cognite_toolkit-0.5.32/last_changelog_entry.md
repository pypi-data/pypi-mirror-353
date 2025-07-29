## cdf 

### Fixed

- When running `cdf dump datamodel` of a data model deployed through the
UI, Toolkit now orders the implements of the views from grandparent,
parent, and so on. This is in case the grandparent has a direct relation
property that the parent overwrites with a new source, the parent source
is used instead of the grandparent source for a child view.

## templates

No changes.